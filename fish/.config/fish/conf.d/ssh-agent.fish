# Persistent ssh-agent shared across fish sessions (until reboot or agent killed)
if status is-interactive
    set -l ssh_env_file ~/.ssh/fish-ssh-agent-env

    if test -f $ssh_env_file
        eval (cat $ssh_env_file) > /dev/null
    end

    if not set -q SSH_AGENT_PID; or not kill -0 $SSH_AGENT_PID 2>/dev/null
        eval (ssh-agent -c) > /dev/null
        echo "setenv SSH_AUTH_SOCK $SSH_AUTH_SOCK; setenv SSH_AGENT_PID $SSH_AGENT_PID;" > $ssh_env_file
        chmod 600 $ssh_env_file
    end

    if not ssh-add -l > /dev/null 2>&1
        ssh-add ~/.ssh/id_ed25519 2>/dev/null
    end
end
