from click.testing import CliRunner
from veridian_atlas.cli.run_query import cli

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
