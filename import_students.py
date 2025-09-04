"""Main script to import students and groups from Excel."""

import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict

from src.importers import ExcelImporter
from src.models import Student, Group, StudentGroup
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/import_{time}.log", level="DEBUG", rotation="10 MB")


class StudentGroupProcessor:
    """Process students and extract groups from Excel data."""
    
    def __init__(self, excel_path: Path):
        """Initialize processor with Excel file path."""
        self.excel_path = excel_path
        self.students: Dict[int, Student] = {}
        self.groups: Dict[int, Group] = {}
        self.relationships: List[StudentGroup] = []
        self.group_name_to_id: Dict[str, int] = {}
        self.next_group_id = 1
    
    def import_data(self) -> pd.DataFrame:
        """Import data from Excel file."""
        logger.info(f"Importing data from {self.excel_path}")
        
        importer = ExcelImporter(self.excel_path)
        df = importer.import_data()
        
        logger.info(f"Imported {len(df)} records")
        return df
    
    def process_students(self, df: pd.DataFrame):
        """Process student records from DataFrame."""
        logger.info("Processing student records...")
        
        for idx, row in df.iterrows():
            try:
                # Create student object
                student = Student(
                    user_id=int(row['user_id']),
                    email=str(row['email']) if pd.notna(row['email']) else '',
                    title=str(row['title']) if pd.notna(row['title']) else None,
                    name=str(row['name']) if pd.notna(row['name']) else None,
                    surname=str(row['surname']) if pd.notna(row['surname']) else None,
                    active=bool(row['active']) if pd.notna(row['active']) else True,
                    newsletter=bool(row['newsletter']) if pd.notna(row['newsletter']) else False,
                    internal_note=str(row['internal_note']) if pd.notna(row['internal_note']) else None,
                    address_street=str(row['address_street']) if pd.notna(row['address_street']) else None,
                    address_city=str(row['address_city']) if pd.notna(row['address_city']) else None,
                    address_zip=str(row['address_zip']) if pd.notna(row['address_zip']) else None,
                    address_country=str(row['address_country']) if pd.notna(row['address_country']) else None
                )
                
                # Process phone number
                if pd.notna(row['address_phone']):
                    student.address_phone = str(int(row['address_phone']))
                
                self.students[student.user_id] = student
                
            except Exception as e:
                logger.error(f"Error processing student at row {idx}: {e}")
        
        logger.success(f"Processed {len(self.students)} students")
    
    def extract_groups(self, df: pd.DataFrame):
        """Extract unique groups from the groups column."""
        logger.info("Extracting groups from data...")
        
        all_groups = set()
        student_groups_mapping = defaultdict(list)
        
        # Process each student's groups
        for idx, row in df.iterrows():
            if pd.notna(row['groups']):
                user_id = int(row['user_id'])
                groups_str = str(row['groups'])
                
                # Split groups by comma
                groups_list = [g.strip() for g in groups_str.split(',') if g.strip()]
                
                for group_name in groups_list:
                    all_groups.add(group_name)
                    student_groups_mapping[user_id].append(group_name)
        
        # Create Group objects
        for group_name in sorted(all_groups):
            if group_name not in self.group_name_to_id:
                group = Group(
                    group_id=self.next_group_id,
                    name=group_name
                )
                self.groups[group.group_id] = group
                self.group_name_to_id[group_name] = group.group_id
                self.next_group_id += 1
        
        logger.success(f"Extracted {len(self.groups)} unique groups")
        
        # Create relationships
        self._create_relationships(student_groups_mapping)
    
    def _create_relationships(self, student_groups_mapping: Dict[int, List[str]]):
        """Create student-group relationships."""
        logger.info("Creating student-group relationships...")
        
        relationship_count = 0
        
        for user_id, group_names in student_groups_mapping.items():
            if user_id in self.students:
                student = self.students[user_id]
                
                for group_name in group_names:
                    group_id = self.group_name_to_id.get(group_name)
                    if group_id:
                        # Add to student's groups
                        student.group_ids.add(group_id)
                        
                        # Add to group's students
                        self.groups[group_id].student_ids.add(user_id)
                        
                        # Create relationship record
                        relationship = StudentGroup(
                            student_id=user_id,
                            group_id=group_id
                        )
                        self.relationships.append(relationship)
                        relationship_count += 1
        
        logger.success(f"Created {relationship_count} student-group relationships")
    
    def generate_statistics(self) -> Dict:
        """Generate statistics about the imported data."""
        stats = {
            'total_students': len(self.students),
            'total_groups': len(self.groups),
            'total_relationships': len(self.relationships),
            'students_with_groups': sum(1 for s in self.students.values() if s.group_ids),
            'students_without_groups': sum(1 for s in self.students.values() if not s.group_ids),
            'groups_by_category': defaultdict(int),
            'largest_groups': [],
            'students_per_group_avg': 0
        }
        
        # Count groups by category
        for group in self.groups.values():
            stats['groups_by_category'][group.category or 'UNCATEGORIZED'] += 1
        
        # Find largest groups
        sorted_groups = sorted(
            self.groups.values(),
            key=lambda g: len(g.student_ids),
            reverse=True
        )
        stats['largest_groups'] = [
            {'name': g.name, 'student_count': len(g.student_ids)}
            for g in sorted_groups[:10]
        ]
        
        # Calculate average students per group
        if self.groups:
            total_enrollments = sum(len(g.student_ids) for g in self.groups.values())
            stats['students_per_group_avg'] = round(total_enrollments / len(self.groups), 2)
        
        return stats
    
    def export_to_json(self, output_dir: Path = Path('data/processed')):
        """Export processed data to JSON files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export students
        students_file = output_dir / 'students.json'
        students_data = [s.to_dict() for s in self.students.values()]
        with open(students_file, 'w', encoding='utf-8') as f:
            json.dump(students_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported students to {students_file}")
        
        # Export groups
        groups_file = output_dir / 'groups.json'
        groups_data = [g.to_dict() for g in self.groups.values()]
        with open(groups_file, 'w', encoding='utf-8') as f:
            json.dump(groups_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported groups to {groups_file}")
        
        # Export relationships
        relationships_file = output_dir / 'student_groups.json'
        relationships_data = [r.to_dict() for r in self.relationships]
        with open(relationships_file, 'w', encoding='utf-8') as f:
            json.dump(relationships_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported relationships to {relationships_file}")
        
        # Export statistics
        stats_file = output_dir / 'import_statistics.json'
        stats = self.generate_statistics()
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported statistics to {stats_file}")
    
    def export_to_csv(self, output_dir: Path = Path('data/processed')):
        """Export processed data to CSV files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export students
        students_df = pd.DataFrame([s.to_dict() for s in self.students.values()])
        students_df['group_ids'] = students_df['group_ids'].apply(lambda x: ','.join(map(str, x)) if x else '')
        students_csv = output_dir / 'students.csv'
        students_df.to_csv(students_csv, index=False, encoding='utf-8')
        logger.info(f"Exported students to {students_csv}")
        
        # Export groups
        groups_df = pd.DataFrame([g.to_dict() for g in self.groups.values()])
        groups_df['student_ids'] = groups_df['student_ids'].apply(lambda x: ','.join(map(str, x)) if x else '')
        groups_csv = output_dir / 'groups.csv'
        groups_df.to_csv(groups_csv, index=False, encoding='utf-8')
        logger.info(f"Exported groups to {groups_csv}")
        
        # Export relationships
        relationships_df = pd.DataFrame([r.to_dict() for r in self.relationships])
        relationships_csv = output_dir / 'student_groups.csv'
        relationships_df.to_csv(relationships_csv, index=False, encoding='utf-8')
        logger.info(f"Exported relationships to {relationships_csv}")
    
    def run(self):
        """Run the complete import process."""
        logger.info("Starting student import process...")
        
        # Import data
        df = self.import_data()
        
        # Process students
        self.process_students(df)
        
        # Extract groups and create relationships
        self.extract_groups(df)
        
        # Generate and display statistics
        stats = self.generate_statistics()
        logger.info("=" * 50)
        logger.info("IMPORT STATISTICS:")
        logger.info(f"Total students: {stats['total_students']}")
        logger.info(f"Total groups: {stats['total_groups']}")
        logger.info(f"Total relationships: {stats['total_relationships']}")
        logger.info(f"Students with groups: {stats['students_with_groups']}")
        logger.info(f"Students without groups: {stats['students_without_groups']}")
        logger.info(f"Average students per group: {stats['students_per_group_avg']}")
        
        logger.info("\nGroups by category:")
        for category, count in stats['groups_by_category'].items():
            logger.info(f"  {category}: {count}")
        
        logger.info("\nTop 10 largest groups:")
        for i, group in enumerate(stats['largest_groups'], 1):
            logger.info(f"  {i}. {group['name']}: {group['student_count']} students")
        
        # Export data
        self.export_to_json()
        self.export_to_csv()
        
        logger.success("Import process completed successfully!")


if __name__ == "__main__":
    processor = StudentGroupProcessor(Path("Flox_persons.xlsx"))
    processor.run()