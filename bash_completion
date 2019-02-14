_wb_completion () {
    local cur prev
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "s b a c n -V -E" -- $cur) )
    elif [[ $COMP_CWORD -eq 2 ]]; then
        case "$prev" in
            "s") COMPREPLY=($(compgen -W "$(wb s)" -- $cur));;
            "b") COMPREPLY=($(compgen -W "$(wb b)" -- $cur));;
            "a") COMPREPLY=($(compgen -W "$(wb a)" -- $cur));;
            "c") COMPREPLY=($(compgen -W "$(wb c)" -- $cur));;
            "n") COMPREPLY=($(compgen -W "$(wb n)" -- $cur));;
        esac
    fi
}
complete -F _wb_completion wb
