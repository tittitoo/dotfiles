function sshk --description 'ssh via YubiKey FIDO2 touch key (portable Homebrew prefix)' --wraps ssh
    set -l ssh_bin (brew --prefix openssh)/bin/ssh
    $ssh_bin -F /dev/null -l infowizard -i ~/.ssh/id_ed25519_sk_touch -o IdentitiesOnly=yes $argv
end
