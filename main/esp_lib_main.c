#include <string.h>
#include <sys/param.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"
#include <pthread.h>

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include <lwip/netdb.h>
#include <stdio.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_system.h>
#include <bmp280.h>
#include <string.h>
//Attenzione a fare i test potrebbero arrivare dati da test precedenti, la rete si comporta male
//No debug bisogna stampare, il topic non viene creato, in chiusura non è gestito
//Comportamento strano al broker, connection reset by peer
#define SDA_GPIO 16
#define SCL_GPIO 15



#define HOST_IP_ADDR "192.168.2.2"


#define PORT 10000
//Cambio questa riga altrimenti non  funziona nulla

#if defined(CONFIG_IDF_TARGET_ESP32S2)
#define APP_CPU_NUM PRO_CPU_NUM
#endif
static void tcp_client_task(void *pvParameters);
static const char *TAG = "example";
pthread_mutex_t payload_mutex;
 char payload[256] = "";
static void bmp280_test(void *pvParamters);

void bmp280_test(void *pvParamters)
{
    bmp280_params_t params;
    bmp280_init_default_params(&params);
    bmp280_t dev;
    memset(&dev, 0, sizeof(bmp280_t));
    printf("\nTask started...\n");
    ESP_ERROR_CHECK(bmp280_init_desc(&dev, BMP280_I2C_ADDRESS_0, 0, SDA_GPIO, SCL_GPIO));
    ESP_ERROR_CHECK(bmp280_init(&dev, &params));

    bool bme280p = dev.id == BME280_CHIP_ID;
    printf("BMP280: found %s\n", bme280p ? "BME280" : "BMP280");

    float pressure, temperature, humidity;
    
    while (1)
    {
        vTaskDelay(1000 / portTICK_PERIOD_MS);
        if (bmp280_read_float(&dev, &temperature, &pressure, &humidity) != ESP_OK)
        {
            printf("Temperature/pressure reading failed\n");
            continue;
        }

        /* float is used in printf(). you need non-default configuration in
         * sdkconfig for ESP8266, which is enabled by default for this
         * example. see sdkconfig.defaults.esp8266
         */
        printf("Pressure: %.2f Pa, Temperature: %.2f C", pressure, temperature);
        
        pthread_mutex_lock(&payload_mutex);
   	    sprintf(payload,"Pr: %.2f Pa, Te: %.2f C", pressure, temperature); //Introduci codifica
        pthread_mutex_unlock(&payload_mutex);
        
        xTaskCreate(tcp_client_task, "tcp_client", 4096, NULL, 5, NULL);
        vTaskDelay(1000 / portTICK_PERIOD_MS);

        if (bme280p)
            printf(", Humidity: %.2f\n", humidity);
        else
            printf("\n");
    }
}



static void tcp_client_task(void *pvParameters)
{
    char rx_buffer[128];
    char addr_str[128];
    int addr_family;
    int ip_protocol;

    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = inet_addr(HOST_IP_ADDR);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(PORT);
    addr_family = AF_INET;
    ip_protocol = IPPROTO_IP;
    inet_ntoa_r(dest_addr.sin_addr, addr_str, sizeof(addr_str) - 1);
    int sock =  socket(addr_family, SOCK_DGRAM, ip_protocol);
    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
    }
    ESP_LOGI(TAG, "Socket created, sending to %s:%d", HOST_IP_ADDR, PORT);
    int err = connect(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
        ESP_LOGE(TAG, "Socket unable to connect: errno %d", errno);
        shutdown(sock, 0);
        close(sock);
        int sock =  socket(addr_family, SOCK_DGRAM, ip_protocol);
        int err = connect(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
        if (err != 0) {
            ESP_LOGE(TAG, "Second time unable to connect, giving up: errno %d", errno);
            esp_restart();
            }
    }
    ESP_LOGI(TAG, "Successfully created socket, sending payload");
    
    pthread_mutex_lock(&payload_mutex);
    err = send(sock, payload, strlen(payload), 0);
    pthread_mutex_unlock(&payload_mutex);

    if (err < 0) {
            ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
    }
    vTaskDelay(500 / portTICK_PERIOD_MS);
    int len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
    // Error occurred during receiving
    if (len < 0) {
        ESP_LOGE(TAG, "recv failed: errno %d", errno);
    }
    // Data received
    else {
        rx_buffer[len] = 0; // Null-terminate whatever we received and treat like a string
            ESP_LOGI(TAG, "Received %d bytes from %s:", len, addr_str);
            ESP_LOGI(TAG, "%s", rx_buffer);
    }
    if (sock != -1) {
        ESP_LOGI(TAG, "Shutting down socket and restarting measurement task...");
        shutdown(sock, 0);
        close(sock);
    }
    vTaskDelete(NULL);
}


void app_main()
{
    ESP_ERROR_CHECK(i2cdev_init());
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
     * Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    ESP_ERROR_CHECK(example_connect());
    xTaskCreatePinnedToCore(bmp280_test, "bmp280_test", configMINIMAL_STACK_SIZE * 8, NULL, 5, NULL, APP_CPU_NUM);
    fflush(stdout);

    xTaskCreate(tcp_client_task, "tcp_client", 4096, NULL, 5, NULL);
    // vTaskDelay(10000 / portTICK_PERIOD_MS);
    // esp_restart();
}

