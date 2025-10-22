
# Jafner/ECU-Calibration
Dotfiles for my car(-ish).

## About
This repository tracks changes to the Engine Control Unit (ECU) calibration file (ROM) for my 2007 Subaru Outback. Its factory engine management microcontroller is a Renesas SH7058.

## References
- [Renesas SH7058](https://www.renesas.com/en/products/sh7058) microcontroller. [Manual](Renesas%20SH7058%20User's%20Manual.pdf).
- [Merp/SubaruDefs](https://github.com/Merp/SubaruDefs) repository of XML files for defining Subaru ROM maps.
- [RomRaider/RomRaider](https://github.com/RomRaider/RomRaider).
- [Tactrix - EcuFlash v1.44](https://www.tactrix.com/index.php?Itemid=58).

## Changelog
### 2025-10-21 - Additional Baselining
- Zero out AVCS advance tables (Cruise, Non-Cruise)
### 2025-10-20 - Sweeping for Warm Idle MTBT
- Set Idle Speed Target (A, B, C) to 900 RPM when ECT > 104F. 
- Set Base Timing Idle maps (A/B, In-Gear/Neutral) to start sweeping from 16.91 deg to 11.64 deg from ECT 104 to 230.
- Set Rev Limit (Fuel Cut) to 6000/5950 RPM. Abundance of caution.
- Equalize requested torque by RPM for the Sport DBW map. Used the curve from 3600 RPM.
### 2025-10-19 - Tuning Ignition Timing; Establish Baseline
- Copy Base Ignition Timing Primary Non-Cruise onto Base Ignition Timing Primary Cruise.
- Copy Knock Correction Advance Max Non-Cruise onto Knock Correction Advance Max Cruise.
- Copy Primary ignition maps onto Reference counterparts.
### 2025-10-18 - Pedal Feel at High RPM
- Rescale Requested Torque (Accelerator Pedal) SI-DRIVE Intelligent Engine Speed (RPM) axis 800-6500 -> 800-6400 with equal intervals (350).
- Rescale and remap Requested Torque (Accelerator Pedal) SI-DRIVE Sport Sharp to handle 800-7200 RPM without cutting Req. Torq. at 6500 RPM.
- Rescale and remap Requested Torque (Accelerator Pedal) SI-DRIVE Sport to drop Req. Torq. gradually above 6000 RPM. 
- Reduce Rev Limit (Fuel Cut) 7000/6975 -> 6700/6650. Prior confidence in high RPM reliability was founded on the mistaken impression that the hard rev limit was ever being used.
- Reduce Speed Limiting (Throttle) SI-DRIVE Intelligent 137/135 -> 75/73 MPH. 
- Reduce Target Boost values above 2400 RPM and 250 Req. Torq. to peak at 12 PSI (from 13.5). Smoothed.
- Slightly smoothed Requested Torque Base (RPM) at top end.

### OEM/Original vs. Initial Commit (2025-10-17).
Comparison between original ROM and calibration at initial commit to this repo.

#### Summary
- Flattened idle speed tables A, B, & C into one. Raised at-temp idle 750 -> 900.
- Disabled DTCs: 
    - P0037 Rear O2 Sensor Low Input
    - P0038 Rear O2 Sensor High Input
    - P0137 Rear O2 Sensor Low Voltage
    - P0138 Rear O2 Sensor High Voltage
    - P0139 Rear O2 Sensor Slow Response
    - P0140 Rear O2 Sensor No Activity
    - P0410 Secondary Air Pump System
    - P0411 Secondary Air Pump Incorrect Flow
    - P0413 Secondary Air Pump A Open
    - P0414 Secondary Air Pump A Shorted
    - P0416 Secondary Air Pump B Open
    - P0417 Secondary Air Pump B Shorted
    - P0418 Secondary Air Pump Relay A
    - P0420 Cat Efficiency Below Threshold
    - P2443 Secondary Air Pump 2 Stuck Closed
- Raised rev limit (fuel cut AKA wasted spark) 6700 -> 7000. Reduced hysteresis 50 -> 25 RPM.
- Copied Sport Sharp DBW throttle map over Sport DBW throttle map. 
- Raised initial/starting Ignition Advance Multiplier (IAM, aka Dynamic Advance Multiplier/DAM) 0.500 -> 1.000.
- Zeroed out Timing Compensation A (IAT) Activation table.
- Smoothed Knock Correction Advance Non-Cruise table. 
- Smoothed and retarded ignition timing across the board in Base Timing Primary Non-Cruise.
- Increased MAF Limit (Maximum) 300 -> 500 g/sec.
- Compressed A/F Learning #1 Airflow Ranges 10-80 g/s -> 5.6-40 g/s.
- Reduced CL to OL Delay_ Primary to 750 -> 0.
- Reduced CL Delay Maximum (Throttle) 108.3% -> 90.0%.
- Flattened CL Delay Maximum Engine Speed (Per Gear) to 2500 RPM.
- Raised Primary Open Loop Fuel Map Switch (IAM) 0.3500 -> 0.7500.
- Leaned out high-load/RPM zone of Primary Open Loop Fueling map 9.65 AFR -> 12.06 AFR.
- Rescaled Engine Speed (RPM) axis of Max Wastegate Duty_ 2000-6400 -> 1500-7000.
- Rescale Engine Speed (RPM) axis of Target Boost_ 800-6400 -> 480-7200.
- Zeroed AF 3 CL Target Compensation Limits.

#### EcuFlash comparison log:
```
[10:41:50.013] --- ROM comparison ---
[10:41:50.013] (ROM 1) | (ROM 2)
[10:41:50.013] filename: Calibration.2025.10.XX.bin | A2UG000N-2007-USDM-Subaru-Legacy-GT-MT.hex
[10:41:50.013] size: 1048576 | 1048576
[10:41:50.041] empty: 27% | 27%
[10:41:50.041] memory model: SH7058 | SH7058
[10:41:50.041] metadata model: A2UG000N | A2UG000N
[10:41:50.041] comparing maps...
[10:41:50.041] table Engine Speed has differences
[10:41:50.041] table Engine Speed has differences
[10:41:50.041] table Primary Open Loop Fueling has differences
[10:41:50.041] table Primary Open Loop Fuel Map Switch (IAM) has differences
[10:41:50.041] table CL to OL Delay_ has differences
[10:41:50.041] table CL Delay Maximum (Throttle) has differences
[10:41:50.041] table CL Delay Maximum Engine Speed (Per Gear) has differences
[10:41:50.041] table A/F Learning #1 Airflow Ranges has differences
[10:41:50.041] table MAF Limit (Maximum) has differences
[10:41:50.041] table Base Timing Primary Non-Cruise has differences
[10:41:50.053] table Knock Correction Advance Max Non-Cruise has differences
[10:41:50.053] table Timing Compensation A (IAT) Activation has differences
[10:41:50.128] table Advance Multiplier (Initial) has differences
[10:41:50.128] table Requested Torque (Accelerator Pedal) SI-DRIVE Sport has differences
[10:41:50.128] table Rev Limit (Fuel Cut) has differences
[10:41:50.128] table Idle Speed Target A has differences
[10:41:50.128] table Idle Speed Target B has differences
[10:41:50.128] table Idle Speed Target C has differences
[10:41:50.128] table (P0037) REAR O2 SENSOR LOW INPUT has differences
[10:41:50.128] table (P0038) REAR O2 SENSOR HIGH INPUT has differences
[10:41:50.128] table (P0137) REAR O2 SENSOR LOW VOLTAGE has differences
[10:41:50.128] table (P0138) REAR O2 SENSOR HIGH VOLTAGE has differences
[10:41:50.128] table (P0139) REAR O2 SENSOR SLOW RESPONSE has differences
[10:41:50.128] table (P0140) REAR O2 SENSOR NO ACTIVITY has differences
[10:41:50.128] table (P0410) SECONDARY AIR PUMP SYSTEM has differences
[10:41:50.128] table (P0411) SECONDARY AIR PUMP INCORRECT FLOW has differences
[10:41:50.128] table (P0413) SECONDARY AIR PUMP A OPEN has differences
[10:41:50.128] table (P0414) SECONDARY AIR PUMP A SHORTED has differences
[10:41:50.128] table (P0416) SECONDARY AIR PUMP B OPEN has differences
[10:41:50.128] table (P0417) SECONDARY AIR PUMP B SHORTED has differences
[10:41:50.128] table (P0418) SECONDARY AIR PUMP RELAY A has differences
[10:41:50.128] table (P0420) CAT EFFICIENCY BELOW THRESHOLD has differences
[10:41:50.128] table (P2443) SECONDARY AIR PUMP 2 STUCK CLOSED has differences
[10:41:50.144] table AF 3 CL Target Compensation Limits has differences
```