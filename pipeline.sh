#!/usr/bin/env sh

APP_NAME="pipeline"
info() {
  logger -p "info" -t "${APP_NAME}" -s "[INFO] $1"
}
warn() {
  logger -p "warn" -t "${APP_NAME}" -s "[WARN] $1"
}
error() {
  logger -p "error" -t "${APP_NAME}" -s "[ERROR] $1"
}
BRANCH_NAME=$(git branch --show-current)

load_branch() {
  for arg in "$@"; do
    case "$arg" in
    *--branch=*)
      BRANCH_NAME=${arg#*--branch=}
      ;;
    help)
      help
      exit 1
      ;;
    *) ;;

    esac
  done
  if [ -z "${BRANCH_NAME}" ]; then
    BRANCH_NAME="develop"
  fi
  info "Selected the next branch=${BRANCH_NAME}"
}

help() {
  echo "arch-specs pipeline Utility MAN"
  echo
  echo "[input parameters]"
  echo "./pipeline.sh <stage1> <stageN> --branch=<branch_name>"
  echo "avaliable stages: build validate_full specs diagrams confluence"
  echo
  echo "[examples]"
  echo "example #1 (execute all stages for the develop branch):"
  echo "./pipeline.sh build specs diagrams confluence"
  echo
  echo "example #2 (execute some stages for the develop branch):"
  echo "./pipeline.sh build specs diagrams"
  echo
  echo "example #3 (execute some stages for the specific branch):"
  echo "./pipeline.sh specs --branch=release-2021-04-14"
  echo
  echo
}

check_command_result_code() {
  # INPUT: $1 - message
  if [ $? -ne 0 ]; then
    error "$1"
    exit 1
  fi
}

stage_build() {
  stage="build"
  LEAST_ONE=1
  info "STAGE[${stage}]: starting..."
  docker-compose down --remove-orphans
  docker-compose build
  check_command_result_code "STAGE[${stage}]: failed."
  info "STAGE[${stage}]: done"
}

stage_specs() {
  stage="specs"
  LEAST_ONE=1
  info "STAGE[${stage}]: starting..."
  export git_branch=$BRANCH_NAME && docker-compose up  specs_generator specs_generator # --exit-code-from
  check_command_result_code "STAGE[${stage}]: failed."
  info "STAGE[${stage}]: done"
}

stage_diagrams() {
  stage="diagrams"
  LEAST_ONE=1
  info "STAGE[${stage}]: starting..."
  export git_branch=$BRANCH_NAME && docker-compose up diagrams_generator diagrams_generator  # --exit-code-from
  check_command_result_code "STAGE[${stage}]: failed."
  info "STAGE[${stage}]: done"
}

stage_confluence() {
  stage="confluence"
  LEAST_ONE=1
  info "STAGE[${stage}]: starting..."
  export git_branch=$BRANCH_NAME && export validate_only_flag="" && docker-compose up confluence_publisher confluence_publisher # --exit-code-from
  check_command_result_code "STAGE[${stage}]: failed."
  info "STAGE[${stage}]: done"
}

stage_confluence_validate() {
  stage="confluence"
  LEAST_ONE=1
  info "STAGE[${stage}]: starting..."
  export git_branch=$BRANCH_NAME && export validate_only_flag="--validate_only" && docker-compose up  confluence_publisher confluence_publisher # --exit-code-from
  check_command_result_code "STAGE[${stage}]: failed."
  info "STAGE[${stage}]: done"
}

execute_stages() {
  for stage in "$@"; do
    case "$stage" in
    *--branch=*)
      continue
      ;;
    "build")
      stage_build
      continue
      ;;
    "specs")
      stage_specs
      continue
      ;;
    "diagrams")
      stage_diagrams
      continue
      ;;
    "confluence")
      stage_confluence
      continue
      ;;
    "validate")
      stage_build
      stage_specs
      continue
      ;;
    "validate_full")
      stage_build
      stage_specs
      stage_confluence_validate
      continue
      ;;

    "all")
      stage_build
      stage_specs
      stage_diagrams
      stage_confluence
      continue
      ;;
    *)
      info "unknown stage: '${stage}'"
      help
      exit 1
      ;;
    esac
  done

  if [ -z "${LEAST_ONE}" ]; then
    warn "Please, set one or more stages"
    help
    exit 1
  fi

}

load_branch "$@"
execute_stages "$@"
exit 0
