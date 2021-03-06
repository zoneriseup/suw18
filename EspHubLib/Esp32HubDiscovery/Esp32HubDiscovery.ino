#include "EspHubDiscovery.h"

#include <WiFi.h>
// #include <Wire.h>
// #include <BH1750.h>
// #include <OneWire.h>
// #include <DallasTemperature.h>

#include "SSD1306.h" // alias for `#include "SSD1306Wire.h"`

SSD1306  display(0x3c, 5, 4);

// preapare reading internal temperature
#ifdef __cplusplus
extern "C" {
#endif
uint8_t temprature_sens_read();
#ifdef __cplusplus
}
#endif
uint8_t temprature_sens_read();

#define MAIN_LOOP_INTERVAL 10000

EspHubDiscovery hub("ESP32_device");

double timer = 0;

void setup()
{
	Serial.begin(115200);

	// init internal display
	display.init();
	display.setContrast(255);
	display.flipScreenVertically();

	hub.handleWifiConnection();
	hub.setCallback(callback);
	hub.setServer("193.179.108.146", 1883);
	hub.setAbilities("['internal_temp', 'hall_sensor', 'display']");
	hub.begin();
}

void loop()
{
	hub.loop();
	if (millis() - timer > MAIN_LOOP_INTERVAL)
	{
		hub.sendData("internal_temp", getInternalTemperature());
		hub.sendData("hall_sensor", hallRead());
		timer = millis();
	}
}

void callback(char *topic, uint8_t *payload, unsigned int length)
{
	Serial.println("callback");
	Serial.println(length);
	display.clear();

	// char *buff;
	// buff = (char *)malloc(length + 1);
	// bzero(buff, length + 1);
	// memcpy(buff, payload, length);

	int16_t px = (int16_t)payload[length - 4];
	int16_t py = (int16_t)payload[length - 3];
	int16_t height = (int16_t)payload[length - 2];
	int16_t width = (int16_t)payload[length - 1];
	Serial.printf("%d, %d, %d %d\n", px, py, height, width);

	display.drawXbm(px, py, width, height, (const char*)payload);
	display.display();

	// for (int i = 0; i < length; i++)
	// {
	// 	Serial.print((int)buff[i]);
	// }
	// Serial.println();
	// free(buff);
}

/// Read internal temperature of ESP core
float getInternalTemperature()
{
	return (temprature_sens_read() - 32) / 1.8;
}
