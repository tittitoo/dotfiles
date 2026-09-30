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
        if test (uname) = Darwin
            # Keychain-backed: passphrase survives reboot without re-prompting.
            #
            # SSH_ASKPASS_REQUIRE=force keeps this from ever blocking a login:
            # without it ssh-add reads the passphrase straight off /dev/tty when
            # the keychain has no entry, freezing the first shell after a reboot
            # on "Enter passphrase for ...". Forcing the askpass path with
            # /usr/bin/false as the helper makes that case fail instantly instead.
            # Store the passphrase once with:
            #   ssh-add --apple-use-keychain ~/.ssh/id_ed25519
            if not env SSH_ASKPASS=/usr/bin/false SSH_ASKPASS_REQUIRE=force \
                    ssh-add --apple-use-keychain ~/.ssh/id_ed25519 2>/dev/null
                echo "ssh key not loaded (no keychain entry) — run: ssh-add --apple-use-keychain ~/.ssh/id_ed25519"
            end
        else
            ssh-add ~/.ssh/id_ed25519 2>/dev/null
        end
    end
end
