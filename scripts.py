"""Scripts."""
import subprocess


def generate_requirements() -> None:
    """Generate requirements.txt file."""
    print("📦 Exportando requirements.txt...")
    subprocess.run(
        ["poetry1.8.3", "export", "--without-hashes", "-f", "requirements.txt", "-o", "requirements.txt"],
        check=True
    )
    print("✅ Archivo requirements.txt generado exitosamente.")
