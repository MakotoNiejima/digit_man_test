from langgraph.types import interrupt

from atguigu.domain.contexts import TaskContext, InterruptedSystemContext, ResumedSystemContext, StartedSystemContext
from atguigu.domain.state import DialogueState
from atguigu.task.command.commands import StartFlowCommand, ResumeFlowCommand, CancelFlowCommand, SetSlotsCommand, \
    Command
from atguigu.task.flow.flows import FlowsList, Flow


class CommandProcessor:
    def run(self,
            commands: list[Command],
            state: DialogueState,
            flows: FlowsList
            ) -> None:
        for command in commands:
            self._apply(command, state, flows)

    def _apply(
            self,
            command: Command,
            state: DialogueState,
            flows: FlowsList
    ) -> None:
        if isinstance(command, StartFlowCommand):
            self._handle_start_flow(command, state, flows)

        elif isinstance(command, SetSlotsCommand):
            self._hand_setslots_flow(command, state, flows)

        elif isinstance(command, ResumeFlowCommand):
            self._hand_resume_flow(command, state, flows)

        elif isinstance(command, CancelFlowCommand):
            self._hand_cancel_flow(command, state, flows)

    def _handle_start_flow(
            self,
            command: StartFlowCommand,
            state: DialogueState,
            flows: FlowsList)-> None:
        state.end_activating_system_task()
        start_flow_id = command.flow
        #防御，不允许启动系统流程
        if start_flow_id.startswith("system_"):
            raise ValueError(f"cannot start with system command flow: '{start_flow_id}'directly")

        #校验，流程必须存在且有起点
        target_flow = flows.get_flow_by_id(start_flow_id)
        if target_flow is None:
            raise ValueError(f"Unknow flow '{start_flow_id}'")
        start_step = target_flow.start_step()
        if start_step is None:
            raise ValueError(f"Start step '{start_flow_id}' has no start step")

        start_business_flow = flows.get_flow_by_id(start_flow_id)

        active_task = state.active_task

        #情况一： 当前有任务进行中
        if active_task is not None:
            if active_task.flow_id == start_flow_id:
                return
            interrupt_flow_id = active_task.flow_id
            interrupt_flow_name = flows.get_flow_by_id(interrupt_flow_id).flow_name
            state.interrupt_activating_task() #栈中存任务

            resumed = state.resume_task(start_flow_id) #尝试恢复
            if resumed is None:
                state.start_active_business_task(TaskContext(
                    flow_id=start_flow_id,
                    step_id=start_business_flow.flow_name,
                ))

            #不论如何，都要激活中断的系统流程,系统流程只走过长白
            interrupt_system_flow: Flow = flows.get_flow_by_id("system_task_interrupt")
            state.start_active_system_task(InterruptedSystemContext(
                system_flow_id="system_task_interrupt",
                system_step_id=interrupt_system_flow.get_start_step().id,
                interrupted_flow_id=interrupt_flow_name,
                started_flow_id=start_flow_id,
                started_flow_name=start_business_flow.flow_name
            ))
        #当前没有运行的系统流程
        else:
            # 如果查询到了当前要开启的业务流程，不用开启业务流程，不用开启开始的系统流程（这个开场白之前已经说过一次）恢复开场白表示出来
            if state.resume_task(start_flow_id):
                resumed_system_flow = flows.get_flow_by_id("system_task_resumed")
                active_task = state.active_task
                state.start_active_system_task(ResumedSystemContext(
                    system_flow_id="system_task_resumed",
                    system_step_id=resumed_system_flow.get_start_step().id,
                    resumed_flow_id=active_task.flow_id,
                    resumed_flow_name=flows.get_flow_by_id(active_task.flow_id).flow_name
                ))
                return

            #如果未查询到要开启的业务流程
            #1.激活当前业务流程
            state.start_active_business_task(TaskContext(
                flow_id=start_flow_id,
                step_id=start_business_flow.get_start_step().id,
            ))
            #2.激活开始系统流程
            start_system_flow = flows.get_flow_by_id("system_task_start")
            state.start_active_system_task(
                StartedSystemContext(
                    system_flow_id="system_task_start",
                    system_step_id=start_system_flow.get_start_step().id,
                    started_flow_id=start_flow_id,
                    started_flow_name=start_business_flow.flow_name
            ))





        pass

