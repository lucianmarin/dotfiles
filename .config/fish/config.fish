set -p PATH /Applications/Postgres.app/Contents/Versions/12/bin
set -p PATH /Applications/TextMate.app/Contents/MacOS
set -p PATH ~/.cargo/bin
set -p PATH /Users/lucian/GitHub/flutter/bin
set -p PATH /usr/local/opt/ruby/bin
set -p PATH /usr/local/lib/ruby/gems/2.7.0/bin
set -p PATH /usr/local/sbin
set -p PATH /usr/local/Cellar/janet/1.13.1/bin

set -gx EDITOR /usr/local/bin/nano

set -gx DOCKER_TLS_VERIFY "1";
set -gx DOCKER_HOST "tcp://192.168.64.2:2376";
set -gx DOCKER_CERT_PATH "/Users/lucian/.docker/machine/machines/default";
set -gx DOCKER_MACHINE_NAME "default";

set fish_prompt_pwd_dir_length 3

set __fish_git_prompt_showdirtystate "yes"
set __fish_git_prompt_showstashstate "yes"
set __fish_git_prompt_showupstream "auto"
set __fish_git_prompt_showuntrackedfiles "yes"
set __fish_git_prompt_showcolorhints "yes"
set __fish_git_prompt_show_informative_status "yes"

set __fish_git_prompt_color_flags blue
set __fish_git_prompt_shorten_branch_len 1
set __fish_git_prompt_shorten_branch_char_suffix ""

set __fish_git_prompt_char_dirtystate "+"
set __fish_git_prompt_char_invalidstate "-"
set __fish_git_prompt_char_stagedstate "→"
set __fish_git_prompt_char_stashstate "↩"
set __fish_git_prompt_char_cleanstate "_"

function fish_prompt
    printf "%s%s " (prompt_pwd) (__fish_git_prompt)
end

function newdir
    mkdir $argv
    cd $argv
end

function newgit
    newdir $argv
    git init 
end
