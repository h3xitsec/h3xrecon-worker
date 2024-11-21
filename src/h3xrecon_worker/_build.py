from pathlib import Path
from typing import Any, Dict

def replace_versions(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hatch build hook to replace version placeholders in pyproject.toml dependencies
    with actual versions from __about__.py
    """
    # Load versions from __about__.py
    about = {}
    about_path = Path(__file__).parent / "__about__.py"
    with open(about_path, "r") as f:
        exec(f.read(), about)

    # Get the dependencies list from config
    dependencies = config.get("project", {}).get("dependencies", [])
    
    # Replace version placeholders in each dependency
    for i, dep in enumerate(dependencies):
        if "___COREVERSION___" in dep:
            dependencies[i] = dep.replace("___COREVERSION___", about["__core_version__"])
        if "___PLUGINVERSION___" in dep:
            dependencies[i] = dep.replace("___PLUGINVERSION___", about["__plugin_version__"])
    
    # Update the config with modified dependencies
    if "project" in config:
        config["project"]["dependencies"] = dependencies
    
    return config