// SenseCAP S2120 (FW v2.0) uplink decoder for ChirpStack v4
// Handles 4A / 4B / 4C frames, CRC-8 validation, sanity checks,
// and gracefully ignores non-measurement uplinks.

function decodeUplink(input) {
  const bytes = input.bytes || [];
  const fPort = input.fPort;
  const warnings = [];
  const errors = [];
  const data = {};

  // Ignore MAC-only or status uplinks
  if (fPort !== 3 || bytes.length === 0) {
    return {
      data: {},
      warnings: ["Non-measurement uplink ignored"],
      errors: []
    };
  }

  // Detect and extract CRC (0xFE in all observed frames)
  let end = bytes.length;
  let crcProvided = null;

  if (bytes[end - 1] === 0xFE) {
    crcProvided = bytes[end - 1];
    end -= 1;
  }

  // Compute CRC-8 (Dallas/Maxim polynomial 0x31)
  if (crcProvided !== null) {
    const crcCalc = crc8(bytes.slice(0, end));
    data.crc_ok = (crcCalc === crcProvided);
    data.crc_provided = crcProvided;
    data.crc_computed = crcCalc;
    if (!data.crc_ok) warnings.push("CRC mismatch");
  }

  let i = 0;
  while (i < end) {
    const frameId = bytes[i];

    // -------------------------
    // 4A FRAME
    // -------------------------
    if (frameId === 0x4A) {
      if (i + 11 > end) {
        warnings.push("Truncated 4A frame");
        break;
      }

      const tempRaw  = s16(bytes[i+1], bytes[i+2]);
      const humRaw   = bytes[i+3];
      const lightRaw = u32(bytes[i+4], bytes[i+5], bytes[i+6], bytes[i+7]);
      const uvRaw    = bytes[i+8];
      const windRaw  = u16(bytes[i+9], bytes[i+10]);

      data.temperature_c   = tempRaw / 10;
      data.humidity_percent = humRaw;
      data.light_lux        = lightRaw;
      data.uv_index         = uvRaw / 10;
      data.wind_speed_m_s   = windRaw / 10;

      // Sanity checks
      if (data.temperature_c < -50 || data.temperature_c > 80)
        warnings.push("Temperature out of expected range");
      if (data.humidity_percent > 100)
        warnings.push("Humidity > 100%");
      if (data.wind_speed_m_s > 60)
        warnings.push("Wind speed unusually high");

      i += 11;
      continue;
    }

    // -------------------------
    // 4B FRAME
    // -------------------------
    if (frameId === 0x4B) {
      if (i + 9 > end) {
        warnings.push("Truncated 4B frame");
        break;
      }

      const windDirRaw = u16(bytes[i+1], bytes[i+2]);
      const rainIntRaw = u32(bytes[i+3], bytes[i+4], bytes[i+5], bytes[i+6]);
      const pressRaw   = u16(bytes[i+7], bytes[i+8]);

      data.wind_direction_deg      = windDirRaw;
      data.rainfall_intensity_mm_h = rainIntRaw / 1000;
      data.pressure_pa             = pressRaw * 10;

      // Sanity checks
      if (data.wind_direction_deg > 360)
        warnings.push("Wind direction > 360°");
      if (data.pressure_pa < 80000 || data.pressure_pa > 110000)
        warnings.push("Pressure out of expected range");

      i += 9;
      continue;
    }

    // -------------------------
    // 4C FRAME
    // -------------------------
    if (frameId === 0x4C) {
      if (i + 7 > end) {
        warnings.push("Truncated 4C frame");
        break;
      }

      const peakWindRaw = u16(bytes[i+1], bytes[i+2]);
      const rainAccRaw  = u32(bytes[i+3], bytes[i+4], bytes[i+5], bytes[i+6]);

      data.peak_wind_gust_m_s  = peakWindRaw / 10;
      data.rain_accumulation_mm = rainAccRaw / 1000;

      // Sanity checks
      if (data.peak_wind_gust_m_s > 60)
        warnings.push("Peak wind gust unusually high");

      i += 7;
      continue;
    }

    // Unknown frame ID
    warnings.push("Unknown frame ID: 0x" + frameId.toString(16));
    break;
  }

  return { data, warnings, errors };
}

// -------------------------
// Helper functions
// -------------------------
function u16(b0, b1) {
  return (b0 << 8) | b1;
}

function s16(b0, b1) {
  const v = u16(b0, b1);
  return (v & 0x8000) ? v - 0x10000 : v;
}

function u32(b0, b1, b2, b3) {
  return ((b0 << 24) | (b1 << 16) | (b2 << 8) | b3) >>> 0;
}

// CRC-8 Dallas/Maxim (poly 0x31, init 0x00)
function crc8(arr) {
  let crc = 0x00;
  for (let b of arr) {
    crc ^= b;
    for (let i = 0; i < 8; i++) {
      crc = (crc & 0x80) ? ((crc << 1) ^ 0x31) : (crc << 1);
      crc &= 0xFF;
    }
  }
  return crc;
}