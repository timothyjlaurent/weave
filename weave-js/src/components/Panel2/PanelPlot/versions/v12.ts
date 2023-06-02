import * as weave from '@wandb/weave/core';
import * as v10 from './v10';
import * as v11 from './v11';

type LazyStringOrNull = weave.Node<{
  type: 'union';
  members: ['string', 'none'];
}>;
type LazyAxisSelection = weave.Node<{type: 'list'; objectType: 'any'}>;

export type SeriesConfig = Omit<
  v11.SeriesConfig,
  'constants' | 'axisSettings'
> & {
  constants: Omit<v11.SeriesConfig['constants'], 'mark'> & {
    mark: LazyStringOrNull | v11.SeriesConfig['constants']['mark'];
  };
};

export const LAZY_PATHS = [
  'series.#.constants.mark' as const, // # means all array indices
  'axisSettings.x.title' as const,
  'axisSettings.y.title' as const,
  'axisSettings.color.title' as const,
  'signals.domain.x' as const,
  'signals.domain.y' as const,
];

export type AxisSettings = {
  x: Omit<v10.AxisSetting, 'title'> & {
    title?: LazyStringOrNull | string;
  };
  y: Omit<v10.AxisSetting, 'title'> & {
    title?: LazyStringOrNull | string;
  };
  color: Omit<v10.AxisSetting, 'title'> & {
    title?: LazyStringOrNull | string;
  };
};

export type Signals = Omit<v11.PlotConfig['signals'], 'domain'> & {
  domain: {
    x?: LazyAxisSelection | v11.PlotConfig['signals']['domain']['x'];
    y?: LazyAxisSelection | v11.PlotConfig['signals']['domain']['y'];
  };
};

export type PlotConfig = Omit<
  v11.PlotConfig,
  'configVersion' | 'series' | 'axisSettings' | 'signals'
> & {
  configVersion: 12;
  series: SeriesConfig[];
  axisSettings: AxisSettings;
  signals: Signals;
};

export type ConcretePlotConfig = Omit<v11.PlotConfig, 'configVersion'> & {
  configVersion: 12;
};

export const migrate = (config: v11.PlotConfig): PlotConfig => {
  return {
    ...config,
    configVersion: 12,
  };
};
