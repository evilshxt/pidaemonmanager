
#!/usr/bin/env bash
echo "Somebody just fuck me already"
echo "POSIX Syntax"

read -p "Enter the name of a process:" process
echo "Searching for process :$process..."
if [ -z "$process" ]; then   #checks if the variable is empty
	echo "Process not found"
	exit 0
fi
sleep 5

ps aux | grep "$process" 2> /dev/null | grep -v grep
process_id=$(pgrep -x $process | head -n 1) # grab the exact process ID

# function to check if the process is a daemon
isDaemon() {
	if  systemctl list-unit-files --type=service --all | grep -q "${process}.service"; then
		sleep 3
		echo "$process is a daemon"
		sleep 2
		status=$(systemctl is-enabled "${process}.service" 2> /dev/null)
		read -p "Do you want to enable(e), disable(d) the daemon or you want to check the status(s)? :" action
		
		case "$action" in
			e|E)
				if [ "$status" = "enabled" ]; then
					echo "Daemon '$process' is already enabled"
					echo "Use 'sudo systemctl disable $process' to disable"
				else
					sudo systemctl enable "${process}.service"
					echo "$process enabled"
				fi
				;;
			s|S)
				sudo systemctl status "${process}.service";;
			d|D)
				if [ "$status" = "disabled" ]; then
					echo "Daemon '$process' is already disabled"
					echo "Use 'sudo systemctl enable $process' to enable"
				else
					sudo systemctl disable "${process}.service"
					echo "$process disabled"
				fi
				;;
			*)
				echo "Invalid choice";;

		esac
	else
		echo "Process is not a daemon"
	fi
}
# run process checks on non-daemons and if interfered by a daemon, run isDaemon...
if [ -z "$process_id" ];then
	echo "No running processes named '$process' found"
	echo "Process might be a daemon....standby"
	isDaemon
	exit 0
fi
read -p "Do you want to terminate the process $process (y/n)?" answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
	kill  $process_id
	echo "Process terminated successfully"
	exit 0
elif [ "$answer" = "n" ] || [ "$answer" = "N" ]; then
	echo "Process still runs"
	exit 0

fi

# /dev/null made this


