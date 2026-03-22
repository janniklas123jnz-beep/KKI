# typed: false
# frozen_string_literal: true

# Homebrew-Formel für das KKI-Paket (Terra-Schwarm Leitstern).
# Zur Verwendung mit einem eigenen Tap:
#   brew tap janniklas123jnz-beep/kki https://github.com/janniklas123jnz-beep/KKI
#   brew install kki
class Kki < Formula
  include Language::Python::Virtualenv

  desc "Kollektive Künstliche Intelligenz — Terra-Schwarm Leitstern Multi-Agenten-Architektur"
  homepage "https://github.com/janniklas123jnz-beep/KKI"
  url "https://github.com/janniklas123jnz-beep/KKI/archive/refs/heads/master.tar.gz"
  version "0.1.0"
  license "MIT"

  depends_on "python@3.14"

  # Kern-Abhängigkeiten (pip-Ressourcen werden beim Build eingebettet)
  resource "networkx" do
    url "https://files.pythonhosted.org/packages/source/n/networkx/networkx-3.4.2.tar.gz"
    sha256 "307c3669428c5362aab27c8a1260aa8f47c4e91d3891f48be0141738d8d053e1"
  end

  resource "numpy" do
    url "https://files.pythonhosted.org/packages/source/n/numpy/numpy-2.2.4.tar.gz"
    sha256 "9ba03692a45d3eef66559efe1d1096c4b9b75c0986b5dff5530c378fb8331d4f"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system python3, "-c", "import kki; print('KKI Terra-Schwarm Leitstern OK')"
  end
end
