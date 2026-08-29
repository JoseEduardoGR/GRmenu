# frozen_string_literal: true

Gem::Specification.new do |spec|
  spec.name          = "grmenu"
  spec.version       = "0.1.4"
  spec.authors       = ["grcode"]
  spec.email         = ["garabatoangelopolis@gmail.com"]

  spec.summary       = "Menu de navegacion por teclado para terminal en modo TTY crudo (flechas + Enter)"
  spec.description   = "GRmenu es una gema ligera para crear menús interactivos de navegación en terminal POSIX (Linux/macOS) usando flechas arriba/abajo y Enter, sin dependencias externas."
  spec.homepage      = "https://github.com/JoseEduardoGR/GRmenu"
  spec.license       = "MIT"
  spec.required_ruby_version = ">= 2.6.0"

  spec.metadata["source_code_uri"] = "https://github.com/JoseEduardoGR/GRmenu"
  spec.metadata["bug_tracker_uri"] = "https://github.com/JoseEduardoGR/GRmenu/issues"
  spec.metadata["changelog_uri"]   = "https://github.com/JoseEduardoGR/GRmenu/commits/main"

  spec.files         = ["GRmenu.rb", "README.md", "LICENSE"]
  spec.require_paths = ["."]
end
