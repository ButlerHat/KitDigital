import os
import asyncio
import streamlit as st
from typing import Callable


def get_robot_command(id_, vars_, robot, tests: list | None =None, include_tags: list | None =None, output_dir=None):
    if tests is None:
        tests = []
    if include_tags is None:
        include_tags = []
    
    robot_path = st.secrets.paths.robot
    robot_script = os.path.join(robot_path, robot)
    result_path = os.path.join(robot_path, "results", id_) if output_dir is None else output_dir
    robot_command = "/opt/conda/condabin/conda run -n robotframework /opt/conda/envs/robotframework/bin/robot " + \
        f'-d "{result_path}" ' + \
        f'-v OUTPUT_DIR:"{result_path}" {"-v " if len(vars_) > 0 else ""}{" -v ".join(vars_)} ' + \
        f'{"-t " if len(tests) > 0 else ""}{" -t ".join(tests)} ' + \
        f'{"-i " if len(include_tags) > 0 else ""}{" -i ".join(include_tags)} ' + \
        f"{robot_script}"
    return robot_command


def get_pabot_command(id_, vars_, robot, include_tags: list | None =None, output_dir=None):
    if include_tags is None:
        include_tags = []
    
    robot_path = st.secrets.paths.robot
    robot_script = os.path.join(robot_path, robot)
    result_path = os.path.join(robot_path, "results", id_) if output_dir is None else output_dir
    robot_command = "/opt/conda/condabin/conda run -n robotframework /opt/conda/envs/robotframework/bin/pabot " + \
        '--testlevelsplit ' + \
        f'-d "{result_path}" ' + \
        f'{"-v " if len(vars_) > 0 else ""}{" -v ".join(vars_)} ' + \
        f'{"-i " if len(include_tags) > 0 else ""}{" -i ".join(include_tags)} ' + \
        f"{robot_script}"
    return robot_command


async def run_robots(ids_args: dict, robot_files: list, timeout=40):
    assert len(ids_args) == len(robot_files) or len(robot_files) == 1, "Number of robots and number of files must be the same"
    tasks = []
    for (id_, args), robot_file in zip(ids_args.items(), robot_files):
        tasks.append(asyncio.create_task(run_robot(id_, args, robot_file, msg_info=f"Running {id_}")))
        await asyncio.sleep(timeout)

    await asyncio.gather(*tasks)

def create_csv(filepath: str):
    """
    Create CSV file with columns: id_execution, robot, status, exception, msg
    id_execution: timestamp to identify the execution
    robot: File without .robot
    status: "FAIL", "SUCCESS", "SKIP", "RETRY"
    exception: Exception like "VariableError" or "Success"
    msg: Message to handle
    """
    with open(filepath, 'w', encoding='UTF8') as f:
        f.write("id_execution,robot,status,exception,msg\n")


async def run_robot(
        id_: str, 
        vars_: list, 
        robot: str, 
        output_dir: str | None = None, 
        callbacks: list[Callable[[int | None, str, dict, dict], None]] | None = None,
        kwargs_callbacks: dict | None = None,
        msg_info=None,
        pabot=False, 
        include_tags: list | None =None
    ):
    """
    Run robot specified in robot variable
    params:
        id: str - folder where store results
        vars: list - list of variables to pass to robot
        robot: str - robot name
        output_dir: str | None - output directory where results stored
        callback: Callable[[dict], None] | None - callback function to call when robot finishes. It receives a dict with the called params
        msg: str - message to show in spinner
    """
    if callbacks is None:
        callbacks = []
    if kwargs_callbacks is None:
        kwargs_callbacks = {}
    if include_tags is None:
        include_tags = []

    robot_path = st.secrets.paths.robot
    result_path = os.path.join(robot_path, "results", id_) if output_dir is None else output_dir
    # If directory does not exist, create it
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    if pabot:
        robot_command = get_pabot_command(id_, vars_, robot, include_tags=include_tags, output_dir=output_dir)
    else:
        robot_command = get_robot_command(id_, vars_, robot, include_tags=include_tags, output_dir=output_dir)

    # Move to robot directory
    print(f"Running {robot_command} \n")
    msg_ = f"Running {robot}" if not msg_info else msg_info

    with st.spinner(msg_):
        proc = await asyncio.create_subprocess_shell(
            f"{robot_command}",
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        ret_val = proc.returncode
        with open(os.path.join(result_path, f'logfile_out_{id_}.txt'), 'w', encoding='UTF8') as f2:
            f2.write(stdout.decode())
            f2.write(stderr.decode())

    if not hasattr(st.session_state, f'log_{id_}'):
        st.session_state[f'log_{id_}'] = False

    for callback in callbacks:
        callback(ret_val, result_path, kwargs_callbacks, {
            "id_": id_,
            "vars_": vars_,
            "robot": robot,
            "output_dir": output_dir,
            "msg_info": msg_info,
            "pabot": pabot,
            "include_tags": include_tags
        })

    return ret_val
