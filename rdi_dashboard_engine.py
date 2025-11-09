"""
RDI Dashboard - Research & Data Insights - COMPLETE VERSION
With enumerator tracking and all quality metrics
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RDIDashboardEngine:
    """
    Complete dashboard for monitoring data quality metrics from ONA platform
    Includes enumerator tracking and performance analysis
    """
    
    def __init__(self, data_path, config=None):
        """
        Initialize the dashboard with data and configuration
        
        Parameters:
        -----------
        data_path : str
            Path to the ONA exported data (CSV format)
        config : dict
            Configuration dictionary with thresholds and settings
        """
        self.data = pd.read_csv(data_path)
        
        # Default configuration
        self.config = config or {
            'min_duration': 30,
            'max_duration': 120,
            'target_districts': [],
            'gps_tolerance': 0.01,
            'target_boundaries': None,
            'required_fields': [],
            'logical_checks': []
        }
        
        if config:
            self.config.update(config)
        
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare and clean the data for analysis"""
        # Convert submission time to datetime if exists
        time_columns = [col for col in self.data.columns if 'time' in col.lower() or 'date' in col.lower()]
        for col in time_columns:
            try:
                self.data[col] = pd.to_datetime(self.data[col])
                # Remove timezone for consistency
                if self.data[col].dt.tz is not None:
                    self.data[col] = self.data[col].dt.tz_localize(None)
            except:
                pass
    
    def calculate_completion_rates(self, district_column='district'):
        """Calculate completion rates by district"""
        if district_column not in self.data.columns:
            print(f"Warning: '{district_column}' column not found")
            return pd.DataFrame()
        
        # Calculate completeness
        if self.config['required_fields']:
            self.data['is_complete'] = self.data[self.config['required_fields']].notna().all(axis=1)
        else:
            self.data['is_complete'] = self.data.notna().mean(axis=1) > 0.8
        
        completion_by_district = self.data.groupby(district_column).agg({
            'is_complete': ['sum', 'count', 'mean']
        }).round(4)
        
        completion_by_district.columns = ['completed', 'total', 'completion_rate']
        completion_by_district['completion_rate'] = (completion_by_district['completion_rate'] * 100).round(2)
        
        return completion_by_district.reset_index()
    
    def analyze_missing_data(self):
        """Analyze missing data patterns"""
        missing_data = pd.DataFrame({
            'field': self.data.columns,
            'missing_count': self.data.isna().sum().values,
            'missing_percentage': (self.data.isna().sum().values / len(self.data) * 100).round(2)
        })
        
        missing_data = missing_data[missing_data['missing_count'] > 0].sort_values(
            'missing_percentage', ascending=False
        )
        
        return missing_data
    
    def flag_interview_durations(self, duration_column='duration_minutes'):
        """Flag interviews with suspicious durations"""
        if duration_column not in self.data.columns:
            print(f"Warning: '{duration_column}' column not found")
            return pd.DataFrame()
        
        min_dur = self.config.get('min_duration', 30)
        max_dur = self.config.get('max_duration', 120)
        
        flagged = self.data[
            (self.data[duration_column] < min_dur) | 
            (self.data[duration_column] > max_dur)
        ].copy()
        
        if len(flagged) > 0:
            flagged['flag_reason'] = flagged[duration_column].apply(
                lambda x: f'Too short (<{min_dur} min)' if x < min_dur else f'Too long (>{max_dur} min)'
            )
        
        return flagged
    
    def check_gps_coordinates(self, lat_column='latitude', lon_column='longitude'):
        """Check GPS coordinate quality"""
        if lat_column not in self.data.columns or lon_column not in self.data.columns:
            print(f"Warning: GPS columns not found")
            return pd.DataFrame()
        
        gps_issues = []
        
        # Missing coordinates
        missing_gps = self.data[self.data[lat_column].isna() | self.data[lon_column].isna()]
        
        # Out of bounds coordinates
        if self.config.get('target_boundaries'):
            bounds = self.config['target_boundaries']
            out_of_bounds = self.data[
                (self.data[lat_column] < bounds.get('lat_min', -90)) |
                (self.data[lat_column] > bounds.get('lat_max', 90)) |
                (self.data[lon_column] < bounds.get('lon_min', -180)) |
                (self.data[lon_column] > bounds.get('lon_max', 180))
            ]
        else:
            out_of_bounds = pd.DataFrame()
        
        # Duplicate coordinates (suspicious)
        tolerance = self.config.get('gps_tolerance', 0.01)
        self.data['gps_rounded'] = (
            self.data[lat_column].round(2).astype(str) + '_' + 
            self.data[lon_column].round(2).astype(str)
        )
        duplicates = self.data[self.data.duplicated('gps_rounded', keep=False)]
        
        return {
            'missing': len(missing_gps),
            'out_of_bounds': len(out_of_bounds),
            'duplicates': len(duplicates)
        }
    
    def analyze_enumerator_performance(self, enumerator_column='enumerator_id',
                                      duration_column='duration_minutes',
                                      lat_column='latitude',
                                      lon_column='longitude'):
        """Analyze enumerator performance and errors"""
        if enumerator_column not in self.data.columns:
            print(f"Warning: '{enumerator_column}' column not found")
            return pd.DataFrame()
        
        enumerator_stats = []
        
        for enum_id in self.data[enumerator_column].dropna().unique():
            enum_data = self.data[self.data[enumerator_column] == enum_id]
            total_interviews = len(enum_data)
            
            # Duration issues
            duration_issues = 0
            if duration_column in self.data.columns:
                min_dur = self.config.get('min_duration', 30)
                max_dur = self.config.get('max_duration', 120)
                duration_issues = (
                    (enum_data[duration_column] < min_dur) |
                    (enum_data[duration_column] > max_dur)
                ).sum()
            
            # GPS issues
            gps_issues = 0
            if lat_column in self.data.columns and lon_column in self.data.columns:
                gps_issues = (enum_data[lat_column].isna() | enum_data[lon_column].isna()).sum()
            
            # Missing data
            missing_data_count = enum_data.isna().sum().sum()
            
            # Completion issues
            if self.config['required_fields']:
                completion_issues = (~enum_data[self.config['required_fields']].notna().all(axis=1)).sum()
            else:
                completion_issues = (~(enum_data.notna().mean(axis=1) > 0.8)).sum()
            
            total_errors = duration_issues + gps_issues + completion_issues
            error_rate = (total_errors / total_interviews * 100) if total_interviews > 0 else 0
            
            enumerator_stats.append({
                'enumerator_id': enum_id,
                'total_interviews': total_interviews,
                'duration_issues': duration_issues,
                'gps_issues': gps_issues,
                'completion_issues': completion_issues,
                'missing_data_count': missing_data_count,
                'total_errors': total_errors,
                'error_rate': round(error_rate, 2)
            })
        
        return pd.DataFrame(enumerator_stats).sort_values('error_rate', ascending=False)
    
    def generate_dashboard(self, output_file='ona_quality_dashboard.html', 
                          district_column='district',
                          duration_column='duration_minutes',
                          lat_column='latitude',
                          lon_column='longitude',
                          enumerator_column='enumerator_id'):
        """
        Generate interactive HTML dashboard with all quality metrics
        
        Parameters:
        -----------
        output_file : str
            Output HTML file path
        district_column : str
            Name of district column
        duration_column : str
            Name of duration column
        lat_column : str
            Name of latitude column
        lon_column : str
            Name of longitude column
        enumerator_column : str
            Name of enumerator column
        """
        # Calculate all metrics
        completion_rates = self.calculate_completion_rates(district_column)
        missing_data = self.analyze_missing_data()
        duration_flags = self.flag_interview_durations(duration_column)
        gps_stats = self.check_gps_coordinates(lat_column, lon_column)
        enumerator_performance = self.analyze_enumerator_performance(
            enumerator_column, duration_column, lat_column, lon_column
        )
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'Completion Rates by District',
                'Interview Duration Distribution',
                'Top 10 Fields with Missing Data',
                'Daily Submission Trends',
                'Enumerator Error Rates',
                'Enumerator Performance Summary',
                'GPS Coordinate Map',
                'Summary Statistics'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'histogram'}],
                [{'type': 'bar'}, {'type': 'scatter'}],
                [{'type': 'bar'}, {'type': 'table'}],
                [{'type': 'mapbox'}, {'type': 'table'}]
            ],
            row_heights=[0.25, 0.25, 0.25, 0.25],
            vertical_spacing=0.12,
            horizontal_spacing=0.15
        )
        
        # 1. Completion Rates by District
        if not completion_rates.empty and district_column in completion_rates.columns:
            fig.add_trace(
                go.Bar(
                    x=completion_rates[district_column],
                    y=completion_rates['completion_rate'],
                    name='Completion Rate',
                    marker_color='#2E86AB',
                    text=completion_rates['completion_rate'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside'
                ),
                row=1, col=1
            )
        
        # 2. Duration Distribution
        if duration_column in self.data.columns:
            valid_durations = self.data[duration_column].dropna()
            if len(valid_durations) > 0:
                fig.add_trace(
                    go.Histogram(
                        x=valid_durations,
                        name='Duration',
                        marker_color='#06A77D',
                        nbinsx=30
                    ),
                    row=1, col=2
                )
        
        # 3. Missing Data
        if not missing_data.empty:
            top_missing = missing_data.head(10)
            fig.add_trace(
                go.Bar(
                    y=top_missing['field'],
                    x=top_missing['missing_percentage'],
                    name='Missing %',
                    orientation='h',
                    marker_color='#F18F01',
                    text=top_missing['missing_percentage'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside'
                ),
                row=2, col=1
            )
        
        # 4. Daily Trends
        time_col = self.config.get('column_mapping', {}).get('submission_time_column', '_submission_time')
        if time_col in self.data.columns:
            try:
                daily_counts = self.data[time_col].dt.date.value_counts().sort_index()
                fig.add_trace(
                    go.Scatter(
                        x=daily_counts.index,
                        y=daily_counts.values,
                        mode='lines+markers',
                        name='Submissions',
                        marker_color='#06A77D',
                        line=dict(width=2)
                    ),
                    row=2, col=2
                )
            except:
                pass
        
        # 5. Enumerator Error Rates
        if not enumerator_performance.empty:
            top_error_enums = enumerator_performance.head(10)
            fig.add_trace(
                go.Bar(
                    y=top_error_enums['enumerator_id'].astype(str),
                    x=top_error_enums['error_rate'],
                    name='Error Rate %',
                    orientation='h',
                    marker_color='#D62828',
                    text=top_error_enums['error_rate'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside'
                ),
                row=3, col=1
            )
        
        # 6. Enumerator Performance Table
        if not enumerator_performance.empty:
            top_enums = enumerator_performance.head(10)
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=['<b>Enumerator</b>', '<b>Interviews</b>', '<b>Duration Issues</b>', 
                               '<b>GPS Issues</b>', '<b>Error Rate %</b>'],
                        fill_color='#D62828',
                        font=dict(color='white', size=11),
                        align='left'
                    ),
                    cells=dict(
                        values=[
                            top_enums['enumerator_id'].astype(str),
                            top_enums['total_interviews'],
                            top_enums['duration_issues'],
                            top_enums['gps_issues'],
                            top_enums['error_rate'].apply(lambda x: f'{x:.1f}%')
                        ],
                        fill_color='#FFE5E5',
                        align='left',
                        font=dict(size=10)
                    )
                ),
                row=3, col=2
            )
        
        # 7. GPS Map
        if lat_column in self.data.columns and lon_column in self.data.columns:
            valid_gps = self.data[
                self.data[lat_column].notna() & self.data[lon_column].notna()
            ]
            
            if len(valid_gps) > 0:
                hover_text = valid_gps[enumerator_column].astype(str) if enumerator_column in valid_gps.columns else 'Location'
                
                fig.add_trace(
                    go.Scattermapbox(
                        lat=valid_gps[lat_column],
                        lon=valid_gps[lon_column],
                        mode='markers',
                        marker=dict(size=8, color='#2E86AB'),
                        name='Interview Locations',
                        text=hover_text
                    ),
                    row=4, col=1
                )
        
        # 8. Summary Statistics
        summary_data = {
            'Metric': [
                'Total Submissions',
                'Completion Rate',
                'Duration Flags',
                'GPS Issues',
                'Total Enumerators',
                'Avg Error Rate',
                'Data Collection Period'
            ],
            'Value': [
                f"{len(self.data):,}",
                f"{completion_rates['completion_rate'].mean():.1f}%" if not completion_rates.empty else 'N/A',
                f"{len(duration_flags):,}",
                f"{gps_stats.get('missing', 0):,}",
                f"{len(enumerator_performance):,}" if not enumerator_performance.empty else 'N/A',
                f"{enumerator_performance['error_rate'].mean():.1f}%" if not enumerator_performance.empty else 'N/A',
                f"{self.data[time_col].min().date()} to {self.data[time_col].max().date()}" if time_col in self.data.columns else 'N/A'
            ]
        }
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['<b>Metric</b>', '<b>Value</b>'],
                    fill_color='#2E86AB',
                    font=dict(color='white', size=12),
                    align='left'
                ),
                cells=dict(
                    values=[summary_data['Metric'], summary_data['Value']],
                    fill_color='#F0F0F0',
                    align='left',
                    font=dict(size=11)
                )
            ),
            row=4, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'RDI Dashboard - Research & Data Insights',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#1a1a1a'}
            },
            showlegend=False,
            height=1600,
            template='plotly_white',
            font=dict(family="Arial, sans-serif")
        )
        
        # Update mapbox
        if lat_column in self.data.columns and lon_column in self.data.columns:
            valid_gps = self.data[
                self.data[lat_column].notna() & self.data[lon_column].notna()
            ]
            if len(valid_gps) > 0:
                fig.update_layout(
                    mapbox=dict(
                        style="open-street-map",
                        center=dict(
                            lat=valid_gps[lat_column].mean(),
                            lon=valid_gps[lon_column].mean()
                        ),
                        zoom=6
                    )
                )
        
        # Save dashboard
        fig.write_html(output_file)
        print(f"\nDashboard saved to: {output_file}")
        
        return fig
    
    def export_quality_report(self, output_file='quality_report.xlsx'):
        """Export comprehensive quality report to Excel"""
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Overview
            overview = pd.DataFrame({
                'Metric': ['Total Submissions', 'Date Range', 'Districts'],
                'Value': [
                    len(self.data),
                    f"{self.data['_submission_time'].min()} to {self.data['_submission_time'].max()}" if '_submission_time' in self.data.columns else 'N/A',
                    self.data['respondent_information/District_id'].nunique() if 'respondent_information/District_id' in self.data.columns else 'N/A'
                ]
            })
            overview.to_excel(writer, sheet_name='Overview', index=False)
            
            # Completion rates
            completion_rates = self.calculate_completion_rates('respondent_information/District_id')
            if not completion_rates.empty:
                completion_rates.to_excel(writer, sheet_name='Completion Rates', index=False)
            
            # Missing data
            missing_data = self.analyze_missing_data()
            if not missing_data.empty:
                missing_data.to_excel(writer, sheet_name='Missing Data', index=False)
            
            # Duration flags
            duration_flags = self.flag_interview_durations('duration_minutes')
            if not duration_flags.empty:
                duration_flags.to_excel(writer, sheet_name='Duration Flags', index=False)
            
            # Enumerator performance
            enumerator_performance = self.analyze_enumerator_performance(
                'enums_information/enumerator_name', 'duration_minutes', 'latitude', 'longitude'
            )
            if not enumerator_performance.empty:
                enumerator_performance.to_excel(writer, sheet_name='Enumerator Performance', index=False)
        
        print(f"Quality report exported to: {output_file}")
