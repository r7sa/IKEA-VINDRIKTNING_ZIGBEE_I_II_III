from typing import Final

from zigpy.profiles import zha
from zigpy.quirks import CustomCluster
from zigpy.quirks.v2 import (
    QuirkBuilder,
    ReportingConfig,
    SensorDeviceClass,
    SensorStateClass,
)
from zigpy.quirks.v2.homeassistant.number import NumberDeviceClass
import zigpy.types as t
from zigpy.zcl.foundation import ZCLAttributeDef
from zigpy.zcl.clusters.general import Basic, AnalogInput
from zigpy.zcl.clusters.measurement import (
    PM25,
    CarbonDioxideConcentration,
    RelativeHumidity,
    TemperatureMeasurement,
)
from zigpy.quirks.v2.homeassistant import (
    UnitOfTime,
    UnitOfLength,
    UnitOfTemperature,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
)

EFEKTA_FOR_YOU = "EfektaLab for you"


class VOCIndex(AnalogInput, CustomCluster):
    name: str = "VOC Index"
    ep_attribute: str = "voc_index"

    class AttributeDefs(AnalogInput.AttributeDefs):
        voc_raw_data: Final = ZCLAttributeDef(id=0x0065, type=t.Single, access="r", mandatory=True)


class PMMeasurement(PM25, CustomCluster):
    class AttributeDefs(PM25.AttributeDefs):
        pm1: Final = ZCLAttributeDef(id=0x00C8, type=t.Single, access="r")
        pm10: Final = ZCLAttributeDef(id=0x00C9, type=t.Single, access="r")
        # general config
        reading_interval: Final = ZCLAttributeDef(id=0x0201, type=t.uint16_t, access="rw")
        # gasstat config
        enable_pm25: Final = ZCLAttributeDef(id=0x0220, type=t.Bool, access="rw")
        high_pm25: Final = ZCLAttributeDef(id=0x0221, type=t.uint16_t, access="rw")
        low_pm25: Final = ZCLAttributeDef(id=0x0222, type=t.uint16_t, access="rw")
        invert_logic_pm25: Final = ZCLAttributeDef(id=0x0225, type=t.Bool, access="rw")


class CO2Measurement(CarbonDioxideConcentration, CustomCluster):

    class AttributeDefs(CarbonDioxideConcentration.AttributeDefs):
        forced_recalibration: Final = ZCLAttributeDef(id=0x0202, type=t.Bool, access="rw")
        automatic_scal: Final = ZCLAttributeDef(id=0x0402, type=t.Bool, access="rw")
        factory_reset_co2: Final = ZCLAttributeDef(id=0x0206, type=t.Bool, access="rw")
        set_altitude: Final = ZCLAttributeDef(id=0x0205, type=t.uint16_t, access="rw")


class TempMeasurement(TemperatureMeasurement, CustomCluster):
    class AttributeDefs(TemperatureMeasurement.AttributeDefs):
        temperature_offset: Final = ZCLAttributeDef(id=0x0210, type=t.int16s, access="rw")


class RHMeasurement(RelativeHumidity, CustomCluster):
    class AttributeDefs(RelativeHumidity.AttributeDefs):
        humidity_offset: Final = ZCLAttributeDef(id=0x0210, type=t.int16s, access="rw")


(
    QuirkBuilder(EFEKTA_FOR_YOU, "IKEA_VINDRIKTNING_EFEKTA III")
    .replaces_endpoint(1, device_type=zha.DeviceType.SIMPLE_SENSOR)
    .replaces_endpoint(2, device_type=zha.DeviceType.SIMPLE_SENSOR)
    .replaces(Basic, endpoint_id=1)
    .replaces(VOCIndex, endpoint_id=1)
    .replaces(PMMeasurement, endpoint_id=1)
    .replaces(CO2Measurement, endpoint_id=1)
    .replaces(TempMeasurement, endpoint_id=2)
    .replaces(RHMeasurement, endpoint_id=2)
    .sensor(
        PMMeasurement.AttributeDefs.pm1.name,
        PMMeasurement.cluster_id,
        endpoint_id=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PM1,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="pm1",
        fallback_name="PM1",
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .sensor(
        PMMeasurement.AttributeDefs.pm10.name,
        PMMeasurement.cluster_id,
        endpoint_id=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PM10,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="pm10",
        fallback_name="PM10",
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .number(
        PMMeasurement.AttributeDefs.reading_interval.name,
        PMMeasurement.cluster_id,
        translation_key="reading_interval",
        fallback_name="Reading Interval",
        unique_id_suffix="reading_interval",
        min_value=1,
        max_value=300,
        device_class=NumberDeviceClass.DURATION,
        unit=UnitOfTime.SECONDS,
    )
    .switch(
        PMMeasurement.AttributeDefs.enable_pm25.name,
        PMMeasurement.cluster_id,
        translation_key="enable_pm25",
        fallback_name="Enable PM2.5 Control",
        unique_id_suffix="enable_pm25",
    )
    .switch(
        PMMeasurement.AttributeDefs.invert_logic_pm25.name,
        PMMeasurement.cluster_id,
        translation_key="invert_logic_pm25",
        fallback_name="Enable invert logic PM2.5 Control",
        unique_id_suffix="invert_logic_pm25",
    )
    .number(
        PMMeasurement.AttributeDefs.low_pm25.name,
        PMMeasurement.cluster_id,
        translation_key="low_pm25",
        fallback_name="Low PM2.5 Border",
        unique_id_suffix="low_pm25",
        min_value=0,
        max_value=1000,
        device_class=SensorDeviceClass.PM1,
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .number(
        PMMeasurement.AttributeDefs.high_pm25.name,
        PMMeasurement.cluster_id,
        translation_key="high_pm25",
        fallback_name="High PM2.5 Border",
        unique_id_suffix="high_pm25",
        min_value=0,
        max_value=1000,
        device_class=SensorDeviceClass.PM10,
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .command_button(
        CO2Measurement.AttributeDefs.factory_reset_co2.name,
        CO2Measurement.cluster_id,
        translation_key="factory_reset_co2",
        fallback_name="Factory Reset CO2 sensor",
        unique_id_suffix="factory_reset_co2",
        endpoint_id=1,
    )
    .command_button(
        CO2Measurement.AttributeDefs.forced_recalibration.name,
        CO2Measurement.cluster_id,
        translation_key="forced_recalibration_co2",
        fallback_name="Start FRC (Perform Forced Recalibration of the CO2 Sensor)",
        unique_id_suffix="forced_recalibration_co2",
        endpoint_id=1,
    )
    .command_button(
        CO2Measurement.AttributeDefs.automatic_scal.name,
        CO2Measurement.cluster_id,
        translation_key="automatic_scal_co2",
        fallback_name="Automatic self calibration CO2",
        unique_id_suffix="automatic_scal_co2",
        endpoint_id=1,
    )
    .number(
        CO2Measurement.AttributeDefs.set_altitude.name,
        CO2Measurement.cluster_id,
        translation_key="set_altitude_co2",
        fallback_name="Set altitude for CO2",
        unique_id_suffix="set_altitude_co2",
        min_value=0,
        max_value=3000,
        device_class=NumberDeviceClass.DISTANCE,
        unit=UnitOfLength.METERS,
    )
    .number(
        TempMeasurement.AttributeDefs.temperature_offset.name,
        TempMeasurement.cluster_id,
        translation_key="temperature_offset",
        fallback_name="Temperature offset",
        unique_id_suffix="temperature_offset",
        min_value=-50,
        max_value=50,
        step=0.1,
        device_class=NumberDeviceClass.TEMPERATURE,
        unit=UnitOfTemperature.CELSIUS,
    )
    .number(
        RHMeasurement.AttributeDefs.humidity_offset.name,
        RHMeasurement.cluster_id,
        translation_key="humidity_offset",
        fallback_name="Humidity offset",
        unique_id_suffix="humidity_offset",
        min_value=-50,
        max_value=50,
        step=1,
        device_class=NumberDeviceClass.HUMIDITY,
        unit=PERCENTAGE,
    )
    .sensor(
        VOCIndex.AttributeDefs.present_value.name,
        VOCIndex.cluster_id,
        endpoint_id=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.AQI,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="voc_index",
        fallback_name="VOC index",
    )
    .sensor(
        VOCIndex.AttributeDefs.voc_raw_data.name,
        VOCIndex.cluster_id,
        state_class=SensorStateClass.MEASUREMENT,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="voc_raw_data",
        fallback_name="VOC RAW data",
    )
    .add_to_registry()
)
