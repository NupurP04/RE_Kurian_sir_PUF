# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 00:56:29 2025

@author: CDWEL_Guest
"""

/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/

#include "project.h"
#include <stdio.h>  

int main(void) 
{
    
    int16 temperature;
    CyGlobalIntEnable; /* Enable global interrupts. */

    /* Start components */
    ADC_SAR_1_Start();
    AMux_1_Start();
    UART_Start();
    
    IDAC8_1_Start();
    //IDAC8_2_Start();

    uint16 adcResult[30];
    uint32 uniqueId[2];

    

    for (;;) 
    {
        

                            
       

        // transmit ADC results
        
        for (uint8 channel =0; channel < 25; channel++)
        {
            AMux_1_Select(channel); // channel 
                                        
            CyDelay(100);
            
            ADC_SAR_1_StartConvert();
            
            /* wait for ADC conversion to complete */
            ADC_SAR_1_IsEndConversion(ADC_SAR_1_WAIT_FOR_RESULT);
        
            /* get ADC result */

            adcResult[channel] = ADC_SAR_1_GetResult16();
            
            ADC_SAR_1_StopConvert();
        }

        UART_PutChar(0x0D);
        UART_PutChar(0x0A); 
        
         // transmit silicon ID
        CyGetUniqueId(uniqueId);
        UART_PutChar((uniqueId[1] >> 8) & 0xFF);
        UART_PutChar(uniqueId[1] & 0xFF);
        
        // transmit temperature
        DieTemp_1_GetTemp(&temperature);            
        UART_PutChar((temperature >> 8) & 0xFF);
        UART_PutChar(temperature & 0xFF);
            
        for (uint8 i =0; i < 25; i++)
        {
        
            // send ADC result
            UART_PutChar((adcResult[i] >> 8) & 0xFF);
            UART_PutChar(adcResult[i] & 0xFF);           

        }
            
            
        /* delimiter for end of transmission cycle (optional) */
        UART_PutChar(0x00);
        UART_PutChar(0xFF);
        UART_PutChar(0xFF);
        
        
    }

}


/* [] END OF FILE */
