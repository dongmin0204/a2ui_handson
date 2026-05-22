type StockChartPoint = {
  label: string;
  price: number;
};

type StockChartSource = {
  title: string;
  url: string;
};

type StockChartResult = {
  symbol: string;
  company_name: string;
  exchange: string;
  currency: string;
  timeframe: string;
  market_summary: string;
  points: StockChartPoint[];
  sources?: StockChartSource[];
};

function formatPrice(price: number, currency: string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(price);
}

function buildLinePath(points: StockChartPoint[]) {
  if (points.length === 0) return "";

  const width = 420;
  const height = 180;
  const padding = 16;
  const prices = points.map((point) => point.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const range = maxPrice - minPrice || 1;

  return points
    .map((point, index) => {
      const x =
        padding + (index * (width - padding * 2)) / Math.max(points.length - 1, 1);
      const y =
        height - padding - ((point.price - minPrice) / range) * (height - padding * 2);
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
}

export function StockChart({
  result,
  themeColor,
  textColor,
}: {
  result: StockChartResult;
  themeColor: string;
  textColor: string;
}) {
  const latestPrice = result.points[result.points.length - 1]?.price;
  const earliestPrice = result.points[0]?.price;
  const change = latestPrice != null && earliestPrice != null ? latestPrice - earliestPrice : 0;
  const up = change >= 0;
  const linePath = buildLinePath(result.points);

  return (
    <div
      className="stage-enter mt-6 mb-4 w-full max-w-3xl rounded-3xl bg-slate-950/85 p-6 shadow-2xl"
      style={{ color: textColor }}
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] opacity-55">
            GOOGLE GROUNDED MARKET SNAPSHOT
          </p>
          <h3 className="mt-2 text-3xl font-semibold">
            {result.company_name} <span className="opacity-50">({result.symbol})</span>
          </h3>
          <p className="mt-2 text-sm opacity-65">
            {result.exchange} · {result.timeframe}
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-semibold">
            {latestPrice != null ? formatPrice(latestPrice, result.currency) : "정보 없음"}
          </div>
          <div
            className="mt-2 text-sm font-medium"
            style={{ color: up ? "#86efac" : "#fda4af" }}
          >
            {up ? "+" : ""}
            {change.toFixed(2)} / {result.timeframe}
          </div>
        </div>
      </div>

      <div
        className="mt-6 overflow-hidden rounded-2xl border border-white/10"
        style={{
          background: `linear-gradient(180deg, ${themeColor}33 0%, rgba(15, 23, 42, 0.12) 100%)`,
        }}
      >
        <svg viewBox="0 0 420 180" className="h-56 w-full">
          <defs>
            <linearGradient id="stock-area" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={themeColor} stopOpacity="0.45" />
              <stop offset="100%" stopColor={themeColor} stopOpacity="0.06" />
            </linearGradient>
          </defs>
          <path d={`${linePath} L 404 164 L 16 164 Z`} fill="url(#stock-area)" />
          <path
            d={linePath}
            fill="none"
            stroke={themeColor}
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {result.points.map((point, index) => {
            const width = 420;
            const height = 180;
            const padding = 16;
            const prices = result.points.map((entry) => entry.price);
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const range = maxPrice - minPrice || 1;
            const x =
              padding +
              (index * (width - padding * 2)) / Math.max(result.points.length - 1, 1);
            const y =
              height -
              padding -
              ((point.price - minPrice) / range) * (height - padding * 2);

            return (
              <g key={`${point.label}-${index}`}>
                <circle cx={x} cy={y} r="4" fill={themeColor} />
                <text
                  x={x}
                  y="174"
                  textAnchor="middle"
                  className="text-[10px]"
                  fill={textColor}
                  opacity="0.65"
                >
                  {point.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <p className="mt-4 text-sm leading-6 opacity-80">{result.market_summary}</p>

      {result.sources && result.sources.length > 0 ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {result.sources.map((source) => (
            <a
              key={source.url}
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="rounded-full px-3 py-1 text-xs transition"
              style={{
                border: `1px solid ${textColor}22`,
                color: textColor,
              }}
            >
              {source.title}
            </a>
          ))}
        </div>
      ) : null}
    </div>
  );
}
