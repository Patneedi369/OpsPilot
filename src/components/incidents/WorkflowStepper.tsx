import type { WorkflowStage } from '../../types';
import { workflowStages } from '../../hooks/useAppState';

interface WorkflowStepperProps {
  current: WorkflowStage;
}

export function WorkflowStepper({ current }: WorkflowStepperProps) {
  const currentIndex = workflowStages.findIndex((stage) => stage.id === current);

  return (
    <div className="workflow">
      {workflowStages.map((stage, index) => {
        const state = index < currentIndex ? 'done' : index === currentIndex ? 'current' : '';
        return (
          <div className="workflow-step" key={stage.id}>
            <div className="workflow-node">
              <div className={`workflow-dot ${state}`} />
              <div className={`workflow-label ${state}`}>{stage.label}</div>
            </div>
            {index < workflowStages.length - 1 ? (
              <div className={`workflow-line ${index < currentIndex ? 'done' : ''}`} />
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
