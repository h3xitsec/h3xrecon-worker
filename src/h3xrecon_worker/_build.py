from hatchling.metadata.plugin.interface import MetadataHookInterface
from pathlib import Path
from typing import Any, Dict

class VersionReplacementHook(MetadataHookInterface):
    def update(self, metadata: Dict[str, Any]) -> None:
        """
        Update the metadata with version replacements
        """
        about = {}
        # Use the root directory provided by Hatch
        about_path = Path(self.root) / "src" / "h3xrecon_worker" / "__about__.py"
        
        print(f"Root directory: {self.root}")
        print(f"Looking for __about__.py at: {about_path}")
        print(f"File exists: {about_path.exists()}")
        
        if not about_path.exists():
            raise FileNotFoundError(f"Could not find __about__.py at {about_path}")
        
        with about_path.open("r") as f:
            exec(f.read(), about)
        
        if "dependencies" in metadata:
            dependencies = metadata["dependencies"]
            
            for i, dep in enumerate(dependencies):
                if "___COREVERSION___" in dep:
                    dependencies[i] = dep.replace("___COREVERSION___", about["__core_version__"])
                if "___PLUGINVERSION___" in dep:
                    dependencies[i] = dep.replace("___PLUGINVERSION___", about["__plugin_version__"])
            
            metadata["dependencies"] = dependencies

if __name__ == "__main__":
    # Test config that mimics your pyproject.toml structure
    test_config = {
        "project": {
            "dependencies": [
                "h3xrecon-core==___COREVERSION___",
                "h3xrecon-plugin==___PLUGINVERSION___"
            ]
        }
    }
    
    # Run the function and print results
    result = VersionReplacementHook(test_config)
    print("Modified config:")
    print(result.metadata)