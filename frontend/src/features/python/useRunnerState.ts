import { useSyncExternalStore } from "react";

import { pythonRunner, type RunnerState } from "./pythonRunner";

export function useRunnerState(): RunnerState {
  return useSyncExternalStore(pythonRunner.subscribe, pythonRunner.getState);
}
