#!/usr/bin/env python3
"""
Disclaimer wrapper for InvestorClaw skill outputs.
Ensures all outputs include required legal disclaimers.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json


class DisclaimerWrapper:
    """Wrap analysis outputs with required disclaimers."""

    DISCLAIMER = "⚠️  EDUCATIONAL ANALYSIS - NOT INVESTMENT ADVICE"
    CONSULT_PROFESSIONAL = "Consult a qualified financial adviser before making any investment decisions"

    @staticmethod
    def wrap_output(data: Dict[str, Any], analysis_type: str = "Portfolio Analysis", compact: bool = False) -> Dict[str, Any]:
        """
        Wrap analysis output with required disclaimers.

        Args:
            data: The actual analysis data to wrap
            analysis_type: Type of analysis (for logging)
            compact: If True, omit static metadata block (~60 token saving for stdout)

        Returns:
            Wrapped output with disclaimer, data, and metadata
        """
        wrapped = {
            "disclaimer": DisclaimerWrapper.DISCLAIMER,
            "is_investment_advice": False,
            "consult_professional": DisclaimerWrapper.CONSULT_PROFESSIONAL,
            "analysis_type": analysis_type,
            "data": data,
            "generated_at": datetime.now().isoformat(),
        }
        if not compact:
            wrapped["metadata"] = {
                "compliance": "All outputs are educational only, not investment recommendations",
                "liability": "User assumes all liability for investment decisions",
                "review": "Review all data with qualified financial professional"
            }
        return wrapped

    @staticmethod
    def wrap_and_save(data: Dict[str, Any], output_file: str, analysis_type: str = "Portfolio Analysis") -> None:
        """
        Wrap output and save to JSON file.

        Args:
            data: The actual analysis data to wrap
            output_file: Path to output JSON file
            analysis_type: Type of analysis
        """
        wrapped = DisclaimerWrapper.wrap_output(data, analysis_type)
        with open(output_file, 'w') as f:
            json.dump(wrapped, f, indent=2, default=str)

    @staticmethod
    def print_disclaimer(stream=None) -> None:
        """Print disclaimer to stdout or custom stream."""
        import sys
        target = stream or sys.stdout
        print(f"\n{DisclaimerWrapper.DISCLAIMER}", file=target)
        print(f"{DisclaimerWrapper.CONSULT_PROFESSIONAL}\n", file=target)

    @staticmethod
    def add_mandatory_fields(output_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add mandatory disclaimer fields to existing output dictionary.
        Used when wrapping already-structured outputs.
        """
        if "disclaimer" not in output_dict:
            output_dict["disclaimer"] = DisclaimerWrapper.DISCLAIMER

        if "is_investment_advice" not in output_dict:
            output_dict["is_investment_advice"] = False

        if "consult_professional" not in output_dict:
            output_dict["consult_professional"] = DisclaimerWrapper.CONSULT_PROFESSIONAL

        if "generated_at" not in output_dict:
            output_dict["generated_at"] = datetime.now().isoformat()

        return output_dict


if __name__ == '__main__':
    # Example usage
    test_data = {
        "holdings": 5,
        "total_value": 100000,
        "cash": 10000
    }

    wrapped = DisclaimerWrapper.wrap_output(test_data, "Test Holdings Analysis")
    print(json.dumps(wrapped, indent=2))
