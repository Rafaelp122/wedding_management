import React from "react";

export const rechartsMock = {
  ResponsiveContainer: ({
    children,
    width,
    height,
  }: {
    children: React.ReactNode;
    width?: string | number;
    height?: string | number;
  }) => <div data-testid="recharts-container" style={{ width, height }}>{children}</div>,
  BarChart: ({
    children,
    data,
  }: {
    children: React.ReactNode;
    data: unknown[];
  }) => <div data-testid="bar-chart" data-items={data.length}>{children}</div>,
  Bar: ({ dataKey, name }: { dataKey: string; name?: string }) => (
    <div data-testid={`bar-${dataKey}`}>{name}</div>
  ),
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  XAxis: ({ dataKey }: { dataKey: string }) => (
    <div data-testid="x-axis" data-datakey={dataKey} />
  ),
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
};
