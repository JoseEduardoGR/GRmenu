# frozen_string_literal: true

Gem::Specification.new do |spec|
  spec.name          = "grmenu"
  spec.version       = "4.0.0"
  spec.authors       = ["grcode"]
  spec.email         = ["garabatoangelopolis@gmail.com"]

  spec.summary       = "Menu de navegacion interactivo para terminal con Banners ASCII 3D, colores y estilos"
  spec.description   = "GRmenu es una gema ligera para crear menus interactivos de navegacion en terminal (Linux/macOS/Windows) usando flechas arriba/abajo y Enter, con soporte para Banners ASCII 3D, paleta de colores y estilos de marco, sin dependencias externas."
  spec.homepage      = "https://github.com/JoseEduardoGR/GRmenu"
  spec.license       = "MIT"
  spec.required_ruby_version = ">= 2.6.0"

  spec.metadata["source_code_uri"] = "https://github.com/JoseEduardoGR/GRmenu"
  spec.metadata["bug_tracker_uri"] = "https://github.com/JoseEduardoGR/GRmenu/issues"
  spec.metadata["changelog_uri"]   = "https://github.com/JoseEduardoGR/GRmenu/commits/main"

  spec.files = Dir.chdir(File.expand_path(__dir__)) do
    Dir["*.{rb,md}", "data/**/*.{json,txt,gr}"].reject { |f| f =~ /\A[aj]\.rb\z/ }
  end
  spec.extra_rdoc_files = ["README.md"]
  spec.rdoc_options     = ["--main", "README.md"]
  spec.require_paths    = ["."]
end
