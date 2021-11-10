import json
import pathlib
import subprocess
import urllib.request

import appdirs


ASCIIDOC_AST_JAR_URL = "https://github.com/alexpdp7/asciidoc-ast/releases/download/v20211106.1/asciidoc-ast-20211106.1.jar"


def ensure_asciidoc_ast_jar():
    path = get_asciidoc_ast_jar_path()
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(ASCIIDOC_AST_JAR_URL, path)


def get_asciidoc_ast_jar_path():
    dirs = appdirs.AppDirs("adoc_check", "net.pdp7")
    return pathlib.Path(dirs.user_cache_dir, ASCIIDOC_AST_JAR_URL.split("/")[-1])


# $ for a in java jre_openjdk javac java_sdk_openjdk ; do sudo update-alternatives --config $a ; done


def parse(path):
    ensure_asciidoc_ast_jar()
    # we capture stderr because the parser is noisy there
    result = subprocess.run(
        ["java", "-jar", get_asciidoc_ast_jar_path(), path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return json.loads(result.stdout)


def walk(node, f):
    follow_children = f(node)
    if not follow_children or not node.get("children"):
        return
    for child in node["children"]:
        walk(child, f)
