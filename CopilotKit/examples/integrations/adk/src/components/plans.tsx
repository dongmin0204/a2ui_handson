import { AgentState } from "@/lib/types";

export interface PlansCardProps {
  state: AgentState;
  setState: (state: AgentState) => void;
}

export function PlansCard({ state, setState }: PlansCardProps) {
  return (
    <div
      className="glass-panel stage-enter p-8 rounded-3xl shadow-xl max-w-2xl w-full"
      style={{ color: state.textColor }}
    >
      <p className="text-center tracking-[0.24em] text-xs mb-3 opacity-70">
        SHARED STATE
      </p>
      <h1 className="text-4xl font-bold mb-2 text-center">
        오늘의 계획
      </h1>
      <p className="text-center mb-6 leading-7 opacity-85">
        에이전트가 추가하거나 정리한 오늘의 계획을 이곳에서 바로 확인할 수 있습니다.
      </p>
      <hr className="my-6 border-current opacity-20" />
      <div className="flex flex-col gap-3">
        {state.plans?.map((plan, index) => (
          <div
            key={index}
            className="bg-white/15 p-4 rounded-2xl relative group hover:bg-white/20 transition-all duration-300"
          >
            <p className="pr-8">{plan}</p>
            <button
              onClick={() =>
                setState({
                  ...state,
                  plans: state.plans?.filter((_, i) => i !== index),
                })
              }
              className="absolute right-3 top-3 opacity-0 group-hover:opacity-100 transition-opacity 
                bg-red-500 hover:bg-red-600 text-white rounded-full h-6 w-6 flex items-center justify-center"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
      {state.plans?.length === 0 && (
        <p className="text-center my-8 opacity-80">
          아직 등록된 계획이 없습니다. 오른쪽 도우미에게 추가를 요청해보세요.
        </p>
      )}
    </div>
  );
}
