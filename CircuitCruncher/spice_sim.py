import os
import datetime
import re

class SpiceSimulator:
    def __init__(self, name, simdir, config, runsim=True):
        self.name = name
        self.simdir = simdir
        self.config = config
        self.runsim = runsim
        self.err = None

    def comment(self, message):
        print(message)

    def warning(self, message):
        print("Warning: " + message)

    def removeFile(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            self.comment(f"Error: {filename} : {e.strerror}")

    def includeSaveSpice(self, savedir, input_file='save.spi'):
        spice_file = os.path.join(self.simdir, self.name + ".spice")
        with open(spice_file, 'r') as file:
            lines = file.readlines()

        control_start = None
        save_all_line = None
        control_end = None

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line == '.control':
                control_start = i
            elif stripped_line.startswith('save all'):
                save_all_line = i
            elif stripped_line == '.endc':
                control_end = i
                break

        if control_start is None or control_end is None:
            raise ValueError("The netlist file does not contain a proper .control/.endc block.")

        # Delete all .include statements within the .control block first for multiple runs 
        i = control_start + 1
        while i < control_end:
            if lines[i].strip().startswith('.include'):
                del lines[i]
                control_end -= 1
            else:
                i += 1

        if save_all_line is not None:
            insert_position = save_all_line + 1
        else:
            insert_position = control_start + 1

        include_path = os.path.join(savedir, input_file)
        include_command = f"    .include {include_path}\n"

        lines.insert(insert_position, include_command)

        with open(spice_file, 'w') as file:
            file.writelines(lines)


    def ngspice(self, ignore=True):
        simOk = True

        if self.runsim:
            tickTime = datetime.datetime.now()

            self.comment(f"Running {self.name}")

            options = ""
            includes = ""
            if "ngspice" in self.config:
                if "options" in self.config["ngspice"]:
                    options = self.config["ngspice"]["options"]
                else:
                    options = ""

            # Remove old simulation results
            rawcmd = f"cd {self.simdir} && rm -f {self.name}*.raw"
            os.system(rawcmd)
            # self.removeFile(self.oname + ".yaml")


            log_file_path = os.path.join(self.simdir, self.name + ".log")
            # Run NGSPICE
            cmd = f"cd {self.simdir}; ngspice {options} {includes} {self.name}.spice 2>&1 |tee {self.name}.log"
            self.comment(cmd)
            try:
                self.err = os.system(cmd)
            except Exception as e:
                print(e)

            # Exit directly if Ctrl-C is pressed
            if self.err == 2:
                exit()

            if self.err > 0:
                simOk = False

            nextTime = datetime.datetime.now()
            self.comment("Corner simulation time : " + str(nextTime - tickTime))
            tickTime = nextTime
        else:
            self.warning(f"Info: Skipping simulation of {self.name}.spice")

         # Print logfile at the end of the run
        if os.path.exists(log_file_path):
            with open(log_file_path) as fi:
                log_content = fi.read()
                print(log_content)
            
            # Check logfile for errors
            errors = [l for l in log_content.splitlines() if re.search("(Error|ERROR):", l) and not re.search("no graphics interface", l)]

            if len(errors) > 0:
                simOk = False
                for line in errors:
                    print(line.strip())
        else:
            self.comment(f"Log file {log_file_path} not found.")

        return simOk if not ignore else True