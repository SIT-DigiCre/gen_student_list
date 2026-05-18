{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";
  };
  outputs =
    inputs@{ self, flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import inputs.systems;
      perSystem =
        { pkgs, ... }:
        {
          devShells.default = pkgs.mkShell {
            packages = [
              (pkgs.python3.withPackages (
                ps: with ps; [
                  pandas
                  pandas-stubs

                  numpy

                  phonenumbers

                  python-docx
                  openpyxl
                ]
              ))
            ];
          };
        };
    };
}
