// Simple sun icon for the weather card
function SunIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className="w-14 h-14 text-yellow-200"
    >
      <circle cx="12" cy="12" r="5" />
      <path
        d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
        strokeWidth="2"
        stroke="currentColor"
      />
    </svg>
  );
}

// Weather card component where the location and themeColor are based on what the agent
// sets via tool calls.
export function WeatherCard({
  location,
  themeColor,
  textColor,
}: {
  location?: string;
  themeColor: string;
  textColor: string;
}) {
  return (
    <div
      style={{ backgroundColor: themeColor, color: textColor }}
      className="stage-enter rounded-2xl shadow-xl mt-6 mb-4 max-w-md w-full"
    >
      <div className="bg-white/20 p-4 w-full">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold capitalize">
              {location}
            </h3>
            <p className="opacity-85">현재 날씨</p>
          </div>
          <SunIcon />
        </div>

        <div className="mt-4 flex items-end justify-between">
          <div className="text-3xl font-bold">70°</div>
          <div className="text-sm opacity-85">맑은 하늘</div>
        </div>

        <div className="mt-4 pt-4 border-t border-current/30">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-xs opacity-75">습도</p>
              <p className="font-medium">45%</p>
            </div>
            <div>
              <p className="text-xs opacity-75">바람</p>
              <p className="font-medium">5 mph</p>
            </div>
            <div>
              <p className="text-xs opacity-75">체감 온도</p>
              <p className="font-medium">72°</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
