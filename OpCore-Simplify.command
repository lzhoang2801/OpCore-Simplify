#!/usr/bin/env bash

# Get the curent directory, the script name
# and the script name with "py" substituted for the extension.
args=( "$@" )
dir="${0%/*}"
script="${0##*/}"
target="${script%.*}.py"

# use_py3:
#   TRUE  = Use if found, use py2 otherwise
#   FALSE = Use py2
#   FORCE = Use py3
use_py3="TRUE"

tempdir=""

compare_to_version () {
    # Compares our OS version to the passed OS version, and
    # return a 1 if we match the passed compare type, or a 0 if we don't.
    # $1 = 0 (equal), 1 (greater), 2 (less), 3 (gequal), 4 (lequal)
    # $2 = OS version to compare ours to
    if [ -z "$1" ] || [ -z "$2" ]; then
        # Missing info - bail.
        return
    fi
    local current_os= comp=
    current_os="$(sw_vers -productVersion)"
    comp="$(vercomp "$current_os" "$2")"
    # Check gequal and lequal first
    if [[ "$1" == "3" && ("$comp" == "1" || "$comp" == "0") ]] || [[ "$1" == "4" && ("$comp" == "2" || "$comp" == "0") ]] || [[ "$comp" == "$1" ]]; then
        # Matched
        echo "1"
    else
        # No match
        echo "0"
    fi
}

set_use_py3_if () {
    # Auto sets the "use_py3" variable based on
    # conditions passed
    # $1 = 0 (equal), 1 (greater), 2 (less), 3 (gequal), 4 (lequal)
    # $2 = OS version to compare
    # $3 = TRUE/FALSE/FORCE in case of match
    if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
        # Missing vars - bail with no changes.
        return
    fi
    if [ "$(compare_to_version "$1" "$2")" == "1" ]; then
        use_py3="$3"
    fi
}

get_remote_py_version () {
    local pyurl= py_html= py_vers= py_num="3"
    pyurl="https://www.python.org/downloads/macos/"
    py_html="$(curl -L $pyurl 2>&1)"
    if [ -z "$use_py3" ]; then
        use_py3="TRUE"
    fi
    if [ "$use_py3" == "FALSE" ]; then
        py_num="2"
    fi
    py_vers="$(echo "$py_html" | grep -i "Latest Python $py_num Release" | awk '{print $8}' | cut -d'<' -f1)"
    echo "$py_vers"
}

download_py () {
    local vers="$1" url=
    clear
    echo "  ###                        ###"
    echo " #     Downloading Python     #"
    echo "###                        ###"
    echo
    if [ -z "$vers" ]; then
        echo "Gathering latest version..."
        vers="$(get_remote_py_version)"
    fi
    if [ -z "$vers" ]; then
        # Didn't get it still - bail
        print_error
    fi
    echo "Located Version:  $vers"
    echo
    echo "Building download url..."
    url="$(curl -L https://www.python.org/downloads/release/python-${vers//./}/ 2>&1 | grep -iE "python-$vers-macos.*.pkg\"" | awk -F'"' '{ print $2 }')"
    if [ -z "$url" ]; then
        # Couldn't get the URL - bail
        print_error
    fi
    echo " - $url"
    echo
    echo "Downloading..."
    echo
    # Create a temp dir and download to it
    tempdir="$(mktemp -d 2>/dev/null || mktemp -d -t 'tempdir')"
    curl "$url" -o "$tempdir/python.pkg"
    if [ "$?" != "0" ]; then
        echo
        echo " - Failed to download python installer!"
        echo
        exit $?
    fi
    echo
    echo "Running python install package..."
    sudo installer -pkg "$tempdir/python.pkg" -target /
    if [ "$?" != "0" ]; then
        echo
        echo " - Failed to install python!"
        echo
        exit $?
    fi
    echo
    vers_folder="Python $(echo "$vers" | cut -d'.' -f1 -f2)"
    if [ -f "/Applications/$vers_folder/Install Certificates.command" ]; then
        # Certs script exists - let's execute that to make sure our certificates are updated
        echo "Updating Certificates..."
        echo
        "/Applications/$vers_folder/Install Certificates.command"
        echo 
    fi
    echo "Cleaning up..."
    cleanup
    echo
    # Now we check for py again
    echo "Rechecking py..."
    downloaded="TRUE"
    clear
    main
}

cleanup () {
    if [ -d "$tempdir" ]; then
        rm -Rf "$tempdir"
    fi
}

print_error() {
    clear
    cleanup
    echo "  ###                      ###"
    echo " #     Python Not Found     #"
    echo "###                      ###"
    echo
    echo "Python is not installed or not found in your PATH var."
    echo
    echo "Please go to https://www.python.org/downloads/macos/"
    echo "to download and install the latest version."
    echo
    exit 1
}

print_target_missing() {
    clear
    cleanup
    echo "  ###                      ###"
    echo " #     Target Not Found     #"
    echo "###                      ###"
    echo
    echo "Could not locate $target!"
    echo
    exit 1
}

format_version () {
    local vers="$1"
    echo "$(echo "$1" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }')"
}

vercomp () {
    # Modified from: https://apple.stackexchange.com/a/123408/11374
    local ver1="$(format_version "$1")" ver2="$(format_version "$2")"
    if [ $ver1 -gt $ver2 ]; then
        echo "1"
    elif [ $ver1 -lt $ver2 ]; then
        echo "2"
    else
        echo "0"
    fi
}

get_local_python_version() {
    # $1 = Python bin name (defaults to python3)
    # Echoes the path to the highest version of the passed python bin if any
    local py_name="$1" max_version= python= python_version= python_path=
    if [ -z "$py_name" ]; then
        py_name="python3"
    fi
    py_list="$(which -a "$py_name" 2>/dev/null)"
    # Walk that newline separated list
    while read python; do
        if [ -z "$python" ]; then
            # Got a blank line - skip
            continue
        fi
        if [ "$check_py3_stub" == "1" ] && [ "$python" == "/usr/bin/python3" ]; then
            # See if we have a valid developer path
            xcode-select -p > /dev/null 2>&1
            if [ "$?" != "0" ]; then
                # /usr/bin/python3 path - but no valid developer dir
                continue
            fi
        fi
        python_version="$(get_python_version $python)"
        if [ -z "$python_version" ]; then
            # Didn't find a py version - skip
            continue
        fi
        # Got the py version - compare to our max
        if [ -z "$max_version" ] || [ "$(vercomp "$python_version" "$max_version")" == "1" ]; then
            # Max not set, or less than the current - update it
            max_version="$python_version"
            python_path="$python"
        fi
    done <<< "$py_list"
    echo "$python_path"
}

get_python_version() {
    local py_path="$1" py_version=
    # Get the python version by piping stderr into stdout (for py2), then grepping the output for
    # the word "python", getting the second element, and grepping for an alphanumeric version number
    py_version="$($py_path -V 2>&1 | grep -i python | cut -d' ' -f2 | grep -E "[A-Za-z\d\.]+")"
    if [ ! -z "$py_version" ]; then
        echo "$py_version"
    fi
}

prompt_and_download() {
    if [ "$downloaded" != "FALSE" ]; then
        # We already tried to download - just bail
        print_error
    fi
    clear
    echo "  ###                      ###"
    echo " #     Python Not Found     #"
    echo "###                      ###"
    echo
    target_py="Python 3"
    printed_py="Python 2 or 3"
    if [ "$use_py3" == "FORCE" ]; then
        printed_py="Python 3"
    elif [ "$use_py3" == "FALSE" ]; then
        target_py="Python 2"
        printed_py="Python 2"
    fi
    echo "Could not locate $printed_py!"
    echo
    echo "This script requires $printed_py to run."
    echo
    while true; do
        read -p "Would you like to install the latest $target_py now? (y/n):  " yn
        case $yn in
            [Yy]* ) download_py;break;;
            [Nn]* ) print_error;;
        esac
    done
}

main() {
    local python= version=
    # Verify our target exists
    if [ ! -f "$dir/$target" ]; then
        # Doesn't exist
        print_target_missing
    fi
    if [ -z "$use_py3" ]; then
        use_py3="TRUE"
    fi
    if [ "$use_py3" != "FALSE" ]; then
        # Check for py3 first
        python="$(get_local_python_version python3)"
    fi
    if [ "$use_py3" != "FORCE" ] && [ -z "$python" ]; then
        # We aren't using py3 explicitly, and we don't already have a path
        python="$(get_local_python_version python2)"
        if [ -z "$python" ]; then
            # Try just looking for "python"
            python="$(get_local_python_version python)"
        fi
    fi
    if [ -z "$python" ]; then
        # Didn't ever find it - prompt
        prompt_and_download
        return 1
    fi
    # Found it - start our script and pass all args
    "$python" "$dir/$target" "${args[@]}"
}

# Check to see if we need to force based on
# macOS version. 10.15 has a dummy python3 version
# that can trip up some py3 detection in other scripts.
# set_use_py3_if "3" "10.15" "FORCE"
downloaded="FALSE"
# Check for the aforementioned /usr/bin/python3 stub if
# our OS version is 10.15 or greater.
check_py3_stub="$(compare_to_version "3" "10.15")"
trap cleanup EXIT
main
