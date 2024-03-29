import platform
import os
import psutil

def get_system_info():
    distro = platform.system()
    kernel = platform.uname().release
    uptime = os.popen("uptime -p").read().strip().split('up ')[-1]

    
 
    try:
        packages = len(os.popen("dpkg -l").readlines()) - 5
    except FileNotFoundError:
        packages = "N/A"

    shell = os.environ['SHELL']
    terminal = os.environ['TERM']
    cpu = platform.processor()
  
    try:
        gpu = os.popen("lspci | grep -i 'VGA\|3D' | cut -d' ' -f 3-").read().strip()
    except FileNotFoundError:
        gpu = "N/A"

    memory = f"{psutil.virtual_memory().used / (1024 ** 3):.2f} GB / {psutil.virtual_memory().total / (1024 ** 3):.2f} GB"

    info = {
        "Distro": distro,
        "Kernel": kernel,
        "Uptime": uptime,
        "Packages": packages,
        "Shell": shell,
        "Terminal": terminal,
        "CPU": cpu,
        "GPU": gpu,
        "Memory": memory
    }

    return info


if __name__ == "__main__":
    system_info = get_system_info()
    
    formatted_info = [f"{key}: {value}" for key, value in system_info.items()]
    
    result = '\n'.join(formatted_info)
    print(result)
