import subprocess


def ping(server, timeout=4000):
    """
    Pings a server
    :param <str:server> The server to ping
    :param [<int:timeout>] The timeout for the ping - defaults to 4000 (4 seconds - windows default)
    :return <int:result> The time of the ping in ms - None if we timed out or failed to get a result
    """
    command = ["ping", "-n", "1", "-w", str(timeout), server]
    output = subprocess.Popen(command, stdout=subprocess.PIPE)
    command_result = [x.decode("utf-8").lstrip().rstrip() for x in output.stdout]

    if(command_result[-1].startswith("Minimum = ")):
        # Format output: Ie, "Minimum = 6ms, Maximum = 6ms, Average = 6ms" -> `int(6)``
        return int(command_result[-1].split(",")[0].split("= ")[1].rstrip("ms"))
