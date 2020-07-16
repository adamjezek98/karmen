; G-Code generated by Simplify3D(R) Version 4.1.2
; Oct 20, 2019 at 7:45:43 PM
; Settings Summary
;   processName,Process1
;   applyToModels,testcubeXYZ
;   profileName,Default (modified)
;   profileVersion,2017-03-01 08:00:00
;   baseProfile,
;   printMaterial,PLA
;   printQuality,Medium
;   printExtruders,
;   extruderName,Primary Extruder
;   extruderToolheadNumber,0
;   extruderDiameter,0.35
;   extruderAutoWidth,0
;   extruderWidth,0.4
;   extrusionMultiplier,0.9
;   extruderUseRetract,1
;   extruderRetractionDistance,1
;   extruderExtraRestartDistance,0
;   extruderRetractionZLift,0
;   extruderRetractionSpeed,1800
;   extruderUseCoasting,0
;   extruderCoastingDistance,0.2
;   extruderUseWipe,0
;   extruderWipeDistance,5
;   primaryExtruder,0
;   layerHeight,0.2
;   topSolidLayers,3
;   bottomSolidLayers,3
;   perimeterOutlines,2
;   printPerimetersInsideOut,1
;   startPointOption,2
;   startPointOriginX,0
;   startPointOriginY,0
;   sequentialIslands,0
;   spiralVaseMode,0
;   firstLayerHeightPercentage,100
;   firstLayerWidthPercentage,100
;   firstLayerUnderspeed,0.5
;   useRaft,0
;   raftExtruder,0
;   raftTopLayers,3
;   raftBaseLayers,2
;   raftOffset,3
;   raftSeparationDistance,0.14
;   raftTopInfill,100
;   aboveRaftSpeedMultiplier,0.3
;   useSkirt,1
;   skirtExtruder,0
;   skirtLayers,1
;   skirtOutlines,2
;   skirtOffset,4
;   usePrimePillar,0
;   primePillarExtruder,999
;   primePillarWidth,12
;   primePillarLocation,7
;   primePillarSpeedMultiplier,1
;   useOozeShield,0
;   oozeShieldExtruder,999
;   oozeShieldOffset,2
;   oozeShieldOutlines,1
;   oozeShieldSidewallShape,1
;   oozeShieldSidewallAngle,30
;   oozeShieldSpeedMultiplier,1
;   infillExtruder,0
;   internalInfillPattern,Rectilinear
;   externalInfillPattern,Rectilinear
;   infillPercentage,20
;   outlineOverlapPercentage,15
;   infillExtrusionWidthPercentage,100
;   minInfillLength,5
;   infillLayerInterval,1
;   internalInfillAngles,45,-45
;   overlapInternalInfillAngles,0
;   externalInfillAngles,45,-45
;   generateSupport,0
;   supportExtruder,0
;   supportInfillPercentage,30
;   supportExtraInflation,0
;   supportBaseLayers,0
;   denseSupportExtruder,0
;   denseSupportLayers,0
;   denseSupportInfillPercentage,70
;   supportLayerInterval,1
;   supportHorizontalPartOffset,0.3
;   supportUpperSeparationLayers,1
;   supportLowerSeparationLayers,1
;   supportType,0
;   supportGridSpacing,4
;   maxOverhangAngle,45
;   supportAngles,0
;   temperatureName,Primary Extruder
;   temperatureNumber,0
;   temperatureSetpointCount,1
;   temperatureSetpointLayers,1
;   temperatureSetpointTemperatures,0
;   temperatureStabilizeAtStartup,1
;   temperatureHeatedBed,0
;   fanLayers,1,2
;   fanSpeeds,0,100
;   blipFanToFullPower,0
;   adjustSpeedForCooling,1
;   minSpeedLayerTime,15
;   minCoolingSpeedSlowdown,20
;   increaseFanForCooling,0
;   minFanLayerTime,45
;   maxCoolingFanSpeed,100
;   increaseFanForBridging,0
;   bridgingFanSpeed,100
;   use5D,1
;   relativeEdistances,0
;   allowEaxisZeroing,1
;   independentExtruderAxes,0
;   includeM10123,0
;   stickySupport,1
;   applyToolheadOffsets,0
;   gcodeXoffset,0
;   gcodeYoffset,0
;   gcodeZoffset,0
;   overrideMachineDefinition,1
;   machineTypeOverride,0
;   strokeXoverride,210
;   strokeYoverride,210
;   strokeZoverride,205
;   originOffsetXoverride,0
;   originOffsetYoverride,0
;   originOffsetZoverride,0
;   homeXdirOverride,-1
;   homeYdirOverride,-1
;   homeZdirOverride,-1
;   flipXoverride,1
;   flipYoverride,-1
;   flipZoverride,1
;   toolheadOffsets,0,0|0,0|0,0|0,0|0,0|0,0
;   overrideFirmwareConfiguration,0
;   firmwareTypeOverride,RepRap (Marlin/Repetier/Sprinter)
;   GPXconfigOverride,r2
;   baudRateOverride,115200
;   overridePrinterModels,0
;   printerModelsOverride
;   startingGcode,G28 ; home all axes
;   layerChangeGcode,
;   retractionGcode,
;   toolChangeGcode,
;   endingGcode,M104 S0 ; turn off extruder,M140 S0 ; turn off bed,M84 ; disable motors
;   exportFileFormat,gcode
;   celebration,0
;   celebrationSong,Random Song
;   postProcessing,
;   defaultSpeed,9000
;   outlineUnderspeed,1
;   solidInfillUnderspeed,1
;   supportUnderspeed,1
;   rapidXYspeed,6000
;   rapidZspeed,600
;   minBridgingArea,50
;   bridgingExtraInflation,0
;   bridgingExtrusionMultiplier,1
;   bridgingSpeedMultiplier,1
;   useFixedBridgingAngle,0
;   fixedBridgingAngle,0
;   applyBridgingToPerimeters,0
;   filamentDiameters,1.75|1.75|1.75|1.75|1.75|1.75
;   filamentPricesPerKg,46|46|46|46|46|46
;   filamentDensities,1.25|1.25|1.25|1.25|1.25|1.25
;   useMinPrintHeight,0
;   minPrintHeight,0
;   useMaxPrintHeight,0
;   maxPrintHeight,0
;   useDiaphragm,0
;   diaphragmLayerInterval,20
;   robustSlicing,1
;   mergeAllIntoSolid,0
;   onlyRetractWhenCrossingOutline,1
;   retractBetweenLayers,1
;   useRetractionMinTravel,0
;   retractionMinTravel,3
;   retractWhileWiping,0
;   onlyWipeOutlines,1
;   avoidCrossingOutline,0
;   maxMovementDetourFactor,3
;   toolChangeRetractionDistance,12
;   toolChangeExtraRestartDistance,-0.5
;   toolChangeRetractionSpeed,600
;   externalThinWallType,0
;   internalThinWallType,2
;   thinWallAllowedOverlapPercentage,10
;   singleExtrusionMinLength,1
;   singleExtrusionMinPrintingWidthPercentage,50
;   singleExtrusionMaxPrintingWidthPercentage,200
;   singleExtrusionEndpointExtension,0.2
;   horizontalSizeCompensation,0
G90
M82
M106 S0
M104 S0 T0
G28 ; home all axes
; process Process1
; layer 1, Z = 0.200
T0
G92 E0.0000
G1 E-1.0000 F1800
; feature skirt
; tool H0.200 W0.400
G1 Z0.200 F600
G1 X50.400 Y53.095 F6000
G1 E0.0000 F1800
G92 E0.0000
G1 X53.095 Y50.400 E0.1141 F4500
G1 X156.905 Y50.400 E3.2216
G1 X159.600 Y53.095 E3.3356
G1 X159.600 Y156.905 E6.4431
G1 X156.905 Y159.600 E6.5572
G1 X53.095 Y159.600 E9.6647
G1 X50.400 Y156.905 E9.7787
G1 X50.400 Y53.095 E12.8862
G92 E0.0000
G1 E-1.0000 F1800
G1 X50.800 Y53.260 F6000
G1 E0.0000 F1800
G92 E0.0000
G1 X53.260 Y50.800 E0.1042 F4500
G1 X156.740 Y50.800 E3.2017
G1 X159.200 Y53.260 E3.3059
G1 X159.200 Y156.740 E6.4034
G1 X156.740 Y159.200 E6.5076
G1 X53.260 Y159.200 E9.6052
G1 X50.800 Y156.740 E9.7093
G1 X50.800 Y53.260 E12.8069
G92 E0.0000
G1 E-1.0000 F1800
; feature inner perimeter
G1 X55.600 Y55.600 F6000
G1 E0.0000 F1800
G92 E0.0000
G1 X154.400 Y55.600 E2.9575 F4500
G1 X154.400 Y154.400 E5.9150
G1 X55.600 Y154.400 E8.8725
G1 X55.600 Y55.600 E11.8300
; feature outer perimeter
G1 X55.200 Y55.200 F6000
G92 E0.0000
G1 X154.800 Y55.200 E2.9814 F4500
G1 X154.800 Y154.800 E5.9629
G1 X55.200 Y154.800 E8.9443
G1 X55.200 Y55.200 E11.9258
; feature inner perimeter
G1 X75.632 Y68.143 F6000
G92 E0.0000
G1 X75.214 Y70.263 E0.0647 F4500
G1 X75.633 Y72.370 E0.1290
G1 X76.784 Y74.086 E0.1908
G1 X78.500 Y75.236 E0.2527
G1 X80.547 Y75.643 E0.3151
G1 X122.121 Y75.643 E1.5596
G1 X76.456 Y131.908 E3.7288
G1 X75.825 Y132.872 E3.7633
G1 X75.367 Y133.966 E3.7988
G1 X75.094 Y135.140 E3.8349
G1 X75.001 Y136.411 E3.8730
G1 X75.549 Y139.115 E3.9556
G1 X77.063 Y141.358 E4.0366
G1 X79.308 Y142.871 E4.1176
G1 X81.991 Y143.412 E4.1996
G1 X131.547 Y143.412 E5.6830
G1 X133.590 Y143.027 E5.7452
G1 X135.308 Y141.921 E5.8064
G1 X136.463 Y140.241 E5.8674
G1 X136.882 Y138.148 E5.9313
G1 X136.464 Y136.043 E5.9956
G1 X135.314 Y134.328 E6.0574
G1 X133.598 Y133.179 E6.1192
G1 X131.550 Y132.772 E6.1817
G1 X89.199 Y132.772 E7.4494

G1 X57.328 Y55.940 E726.2060
G1 X55.940 Y57.328 E726.2648
G1 X55.940 Y56.762 E726.2817
G1 X56.762 Y55.940 E726.3165
G1 X56.196 Y55.940 E726.3335
G1 X55.940 Y56.196 E726.3443
G92 E0.0000
G1 E-1.0000 F1800
; layer end
M104 S0 ; turn off extruder
M140 S0 ; turn off bed
M84 ; disable motors
; Build Summary
;   Build time: 7 hours 37 minutes
;   Filament length: 90037.5 mm (90.04 m)
;   Plastic volume: 216565.55 mm^3 (216.57 cc)
;   Plastic weight: 270.71 g (0.60 lb)
;   Material cost: 12.45
