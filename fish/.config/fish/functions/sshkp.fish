function sshkp --description 'ssh via YubiKey FIDO2 key (portable Homebrew prefix)' --wraps ssh
    set -l ssh_bin (brew --prefix openssh)/bin/ssh
    $ssh_bin -F /dev/null -l infowizard -i ~/.ssh/id_ed25519_sk_yubikey -o IdentitiesOnly=yes $argv
end
