import argparse
from pathlib import Path

from .io import load_jsonl, write_json
from .report import render_html
from .runner import evaluate_suite


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate grounded LLM responses")
    parser.add_argument("dataset", help="JSONL dataset path")
    parser.add_argument("--json", dest="json_output", help="Write JSON report")
    parser.add_argument("--html", dest="html_output", help="Write HTML report")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = evaluate_suite(load_jsonl(args.dataset))
    if args.json_output:
        write_json(report.model_dump(mode="json"), args.json_output)
    if args.html_output:
        destination = Path(args.html_output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_html(report))
    print(report.model_dump_json(indent=2))
    return 0 if report.summary.pass_rate == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
