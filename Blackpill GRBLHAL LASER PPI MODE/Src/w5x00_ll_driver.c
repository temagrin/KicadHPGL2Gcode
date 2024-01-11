/**
 * Copyright (c) 2022 WIZnet Co.,Ltd
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include "w5x00_ll_driver.h"

#if ETHERNET_ENABLE && (_WIZCHIP_ == W5100S || _WIZCHIP_ == W5500)

#include <stdio.h>

#include "spi.h"

#include "socket.h"
#if _WIZCHIP_ == W5500
#include "W5500/w5500.h"
#endif

#ifndef WIZCHIP_SPI_PRESCALER
#define WIZCHIP_SPI_PRESCALER SPI_BAUDRATEPRESCALER_4
#endif

typedef struct {
    GPIO_TypeDef *port;
    uint16_t pin;
} st_gpio_t;

static struct {
    st_gpio_t cs;
    st_gpio_t rst;
} hw;
static uint32_t prescaler = 0;

static void (*irq_callback)(void);
static volatile bool spin_lock = false;

static void wizchip_select (void)
{
    if(prescaler != WIZCHIP_SPI_PRESCALER)
        prescaler = spi_set_speed(WIZCHIP_SPI_PRESCALER);

    DIGITAL_OUT(hw.cs.port, hw.cs.pin, 0);
}

static void wizchip_deselect (void)
{
    DIGITAL_OUT(hw.cs.port, hw.cs.pin, 1);

    if(prescaler != WIZCHIP_SPI_PRESCALER)
        spi_set_speed(prescaler);
}

static void wizchip_critical_section_lock(void)
{
    while(spin_lock);

    spin_lock = true;
}

static void wizchip_critical_section_unlock(void)
{
    spin_lock = false;
}

static bool wizchip_gpio_interrupt_callback (uint_fast8_t id, bool level)
{
    irq_callback();

    return true;
}

static void add_pin (xbar_t *gpio, void *data)
{
  if(gpio->group == PinGroup_SPI) switch(gpio->function) {

        case Output_SPICS:
            hw.cs.port = (GPIO_TypeDef *)gpio->port;
            hw.cs.pin = gpio->pin;
//            hal.periph_port.set_pin_description(gpio->function, gpio->group, "WizNet W5x00 CS");
            break;

        case Output_SPIRST:
            hw.rst.port = (GPIO_TypeDef *)gpio->port;
            hw.rst.pin = gpio->pin;
//            hal.periph_port.set_pin_description(gpio->function, gpio->group, "WizNet W5x00 Reset");
            break;

        default:
            break;
    }
}

// Public functions

void wizchip_reset (void)
{
    if(hw.rst.port) {
        DIGITAL_OUT(hw.rst.port, hw.rst.pin, 0);
        hal.delay_ms(2, NULL);
        DIGITAL_OUT(hw.rst.port, hw.rst.pin, 1);
        hal.delay_ms(10, NULL);
    }
}

wizchip_init_err_t wizchip_initialize (void)
{
    hal.enumerate_pins(true, add_pin, NULL);

    // if(hw.cs.port == NULL)
    //    return error.

    wizchip_deselect();

    spi_init();
    spi_set_speed(WIZCHIP_SPI_PRESCALER);

    wizchip_reset();

    reg_wizchip_cris_cbfunc(wizchip_critical_section_lock, wizchip_critical_section_unlock);
    reg_wizchip_cs_cbfunc(wizchip_select, wizchip_deselect);
    reg_wizchip_spi_cbfunc(spi_get_byte, spi_put_byte);
#ifndef USE_SPI_DMA
    reg_wizchip_spiburst_cbfunc(spi_read, spi_write);
#endif

    /* W5x00 initialize */

#if (_WIZCHIP_ == W5100S)
    uint8_t memsize[2][4] = {{8, 0, 0, 0}, {8, 0, 0, 0}};
#elif (_WIZCHIP_ == W5500)
    uint8_t memsize[2][8] = {{8, 0, 0, 0, 0, 0, 0, 0}, {8, 0, 0, 0, 0, 0, 0, 0}};
#endif

    if(ctlwizchip(CW_INIT_WIZCHIP, (void *)memsize) == -1)
        return WizChipInit_MemErr;

#if _WIZCHIP_ == W5100 ||  _WIZCHIP_ == W5200
    int8_t link_status;
    if (ctlwizchip(CW_GET_PHYLINK, (void *)&link_status) == -1)
        return WizChipInit_UnknownLinkStatus;
#endif

#if (_WIZCHIP_ == W5100S)
    return getVER() == 0x51 ? WizChipInit_OK : WizChipInit_WrongChip;
#elif (_WIZCHIP_ == W5500)
    return getVERSIONR() == 0x04 ? WizChipInit_OK : WizChipInit_WrongChip;
#endif
}

void network_initialize (wiz_NetInfo net_info)
{
    ctlnetwork(CN_SET_NETINFO, (void *)&net_info);
}

bool wizchip_gpio_interrupt_initialize (uint8_t socket, void (*callback)(void))
{
    int ret_val;
    uint16_t reg_val = SIK_RECEIVED; //(SIK_CONNECTED | SIK_DISCONNECTED | SIK_RECEIVED | SIK_TIMEOUT); // except SendOK

    if((ret_val = ctlsocket(socket, CS_SET_INTMASK, (void *)&reg_val)) == SOCK_OK) {

#if (_WIZCHIP_ == W5100S)
        reg_val = (1 << socket);
#elif (_WIZCHIP_ == W5500)
        reg_val = ((1 << socket) << 8);
#endif
        if(ctlwizchip(CW_SET_INTRMASK, (void *)&reg_val) == 0) {
            irq_callback = callback;
            hal.irq_claim(IRQ_SPI, 0, wizchip_gpio_interrupt_callback);
        } else
            ret_val = SOCK_FATAL;
    }

    return ret_val == SOCK_OK;
}

#endif // ETHERNET_ENABLE && defined(_WIZCHIP_)
