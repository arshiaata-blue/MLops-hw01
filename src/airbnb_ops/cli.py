# importing requirements and our self-created modoules
import typer
from pathlib import Path
from airbnb_ops.config import PipelineConfig
from airbnb_ops.extract import read_csv_checked
from airbnb_ops.pii import handle_pii
from airbnb_ops.transform import build_neighbourhood_summary
from airbnb_ops.validate import validate_summary

# Creaating CLI app
app = typer.Typer()

# defining run as command
@app.command(name="run")
def run_pipeline():
    # Adding whatever we've done so far

    # Configurations
    config = PipelineConfig()
    
    # read and check CSV
    listings = read_csv_checked(config.listings_path)
    segments = read_csv_checked(config.segments_path)
    
    # Managing PII
    listings = handle_pii(listings)
    
    # Transformations
    summary = build_neighbourhood_summary(listings, segments)
    
    # Validation
    validate_summary(summary)
    
    # Saving output as CSV
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(config.output_path, index=False)
    
    # Reporting
    config.report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config.report_path, 'w') as f:
        f.write(f"# Airbnb Ops Run Report for the **SCARED CHICKEN**\n\n")
        f.write(f"**Output file:** `{config.output_path}`\n\n")
        f.write(f"**Number of neighbourhoods:** {len(summary)}\n\n")
        f.write(f"**Columns:** {list(summary.columns)}\n\n")
        f.write(f"**Sample:**\n\n")
        f.write(summary.head(3).to_string(index=False))
    
    # Where are my outputs??
    typer.echo(f"Done! Output: {config.output_path}")
    typer.echo(f"Report: {config.report_path}")

if __name__ == "__main__":
    app()