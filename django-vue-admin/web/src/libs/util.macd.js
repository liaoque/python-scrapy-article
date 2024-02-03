import log from "@/libs/util.log";

const macd = {}

macd.calculateMACD = function calculateMACD(data, shortPeriod = 12, longPeriod = 26, signalPeriod = 9) {
  const EMA12 = [];
  const EMA26 = [];
  const DIF = [];
  const DEA = [];
  const MACD = [];

  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      EMA12[i] = data[i];
      EMA26[i] = data[i];
    } else {
      EMA12[i] = (EMA12[i - 1] * (shortPeriod - 1) + data[i]) / shortPeriod;
      EMA26[i] = (EMA26[i - 1] * (longPeriod - 1) + data[i]) / longPeriod;
    }

    DIF[i] = EMA12[i] - EMA26[i];

    if (i === 0) {
      DEA[i] = DIF[i];
    } else {
      DEA[i] = (DEA[i - 1] * (signalPeriod - 1) + DIF[i]) / signalPeriod;
    }

    MACD[i] = (DIF[i] - DEA[i]) * 2;
  }

  return {
    EMA12,
    EMA26,
    DIF,
    DEA,
    MACD,
  };
}

export default macd
