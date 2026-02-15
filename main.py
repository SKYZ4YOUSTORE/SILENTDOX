#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SILENTDOX - OSINT Intelligence Gathering Tool
Version: 3.1.0 (Nickname-Free Logic)
Author: Voidsz_GPT
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from colorama import init, Fore, Style
from tabulate import tabulate
from rapidfuzz import fuzz, process

# Initialize colorama
init(autoreset=True)

# ==================== CONFIGURATION ====================
DATABASE_DIR = "database"
REQUIRED_FIELDS = [
    "Nama", "Alamat", "Gender", "Tanggal Lahir", "Jabatan",
    "Nama Ibu", "NIK", "NIP", "NOMOR REKENING", "NISN",
    "Nomor Hp", "Email", "Nomor AYAH", "Nomor IBU"
]

# Mapping field variations to standardized names
FIELD_MAPPING = {
    # Nama variations
    "nama": "Nama", "name": "Nama", "nama lengkap": "Nama",
    "nama_lengkap": "Nama", "full_name": "Nama", "nama_lgkp": "Nama",
    "nama lgkp": "Nama",
    
    # Alamat variations
    "alamat": "Alamat", "address": "Alamat", "domisili": "Alamat",
    "address_full": "Alamat",
    
    # Gender variations
    "gender": "Gender", "jenis_kelamin": "Gender", "jenis klmin": "Gender",
    "sex": "Gender", "jk": "Gender",
    
    # Tanggal Lahir variations
    "tanggal_lahir": "Tanggal Lahir", "tgl_lahir": "Tanggal Lahir",
    "birthdate": "Tanggal Lahir", "tgl_lhr": "Tanggal Lahir",
    "tgl lahir": "Tanggal Lahir", "tanggal lahir": "Tanggal Lahir",
    "birth_date": "Tanggal Lahir",
    
    # Jabatan variations
    "jabatan": "Jabatan", "position": "Jabatan", "role": "Jabatan",
    "pangkat": "Jabatan", "tugas": "Jabatan", "title": "Jabatan",
    
    # Nama Ibu variations
    "nama_ibu": "Nama Ibu", "ibu": "Nama Ibu",
    "nama ibu kandung": "Nama Ibu", "nama_lgkp_ibu": "Nama Ibu",
    "nama lgkp ibu": "Nama Ibu", "mother_name": "Nama Ibu",
    
    # NIK variations
    "nik": "NIK", "no_ktp": "NIK", "ktp": "NIK",
    "identity_number": "NIK", "nik_ktp": "NIK", "id_card": "NIK",
    
    # NIP variations
    "nip": "NIP", "employee_id": "NIP", "pegawai_id": "NIP",
    "nip_pegawai": "NIP",
    
    # NOMOR REKENING variations
    "nomor_rekening": "NOMOR REKENING", "no_rek": "NOMOR REKENING",
    "rekening": "NOMOR REKENING", "bank_account": "NOMOR REKENING",
    "no_rek_pegawai": "NOMOR REKENING", "account_number": "NOMOR REKENING",
    
    # NISN variations
    "nisn": "NISN", "student_id": "NISN", "no_induk_siswa": "NISN",
    "national_student_id": "NISN",
    
    # Nomor HP variations
    "nomor_hp": "Nomor Hp", "no_hp": "Nomor Hp", "phone": "Nomor Hp",
    "hp": "Nomor Hp", "phone_number": "Nomor Hp", "contact": "Nomor Hp",
    "sms_phone": "Nomor Hp",
    
    # Email variations
    "email": "Email", "mail": "Email", "e_mail": "Email",
    
    # Nomor AYAH variations
    "nomor_ayah": "Nomor AYAH", "no_ayah": "Nomor AYAH",
    "father_phone": "Nomor AYAH", "phone_ayah": "Nomor AYAH",
    "hp_ayah": "Nomor AYAH",
    
    # Nomor IBU variations
    "nomor_ibu": "Nomor IBU", "no_ibu": "Nomor IBU",
    "mother_phone": "Nomor IBU", "phone_ibu": "Nomor IBU",
    "hp_ibu": "Nomor IBU",
}

# ==================== UTILITY FUNCTIONS ====================

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display SilentDox banner"""
    banner = f"""
{Fore.RED}███████╗██╗██╗     ███████╗███╗   ██╗████████╗██████╗  ██████╗ ██╗  ██╗
{Fore.RED}██╔════╝██║██║     ██╔════╝████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗╚██╗██╔╝
{Fore.RED}███████╗██║██║     █████╗  ██╔██╗ ██║   ██║   ██║  ██║██║   ██║ ╚███╔╝ 
{Fore.RED}╚════██║██║██║     ██╔══╝  ██║╚██╗██║   ██║   ██║  ██║██║   ██║ ██╔██╗ 
{Fore.RED}███████║██║███████╗███████╗██║ ╚████║   ██║   ██████╔╝╚██████╔╝██╔╝ ██╗
{Fore.RED}╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝

{Fore.CYAN}███████████████████████████████████████████████████████████████████████

{Fore.BLUE}                          SILENT - DOXING
{Fore.GREEN}                       CreateBy : @TheMrSilent

{Fore.CYAN}███████████████████████████████████████████████████████████████████████
"""
    print(banner)

def get_database_files() -> List[Path]:
    """Get all JSON files in database directory"""
    db_path = Path(DATABASE_DIR)
    if not db_path.exists():
        print(f"{Fore.RED}[!] Database directory not found: {DATABASE_DIR}")
        return []
    return list(db_path.glob("*.json"))

def load_json_file(file_path: Path) -> List[Dict]:
    """Load and parse JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both list and dict formats
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                return []
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Error loading {file_path.name}: {e}")
        return []

def normalize_value(value: Any) -> str:
    """Convert any value to string and clean it"""
    if value is None:
        return ""
    return str(value).strip().upper()

def extract_name(record: Dict) -> str:
    """Extract name from record using various possible keys"""
    record_upper = {k.upper(): v for k, v in record.items()}
    
    # Priority order for name keys
    name_keys = [
        "NAMA", "NAME", "NAMA LENGKAP", "NAMA_LENGKAP",
        "FULL_NAME", "NAMA_LGKP", "NAMA LGKP", "NAMA LENGKAP",
        "PEGAWAI", "EMPLOYEE", "NAMA_PEGAWAI"
    ]
    
    for key in name_keys:
        if key in record_upper:
            val = record_upper[key]
            if val and str(val).strip():
                return normalize_value(val)
    
    # If no direct match, try case-insensitive search
    for k, v in record.items():
        if any(name_word in k.upper() for name_word in ["NAMA", "NAME"]):
            if v and str(v).strip():
                return normalize_value(v)
    
    return ""

def standardize_record(record: Dict, source_file: str) -> Dict:
    """Convert record to standardized format with all required fields"""
    std_record = {field: "" for field in REQUIRED_FIELDS}
    std_record["_source"] = source_file  # Add source tracking
    
    # Try to extract name first
    extracted_name = extract_name(record)
    if extracted_name:
        std_record["Nama"] = extracted_name
    
    # Map all other fields
    for orig_key, orig_value in record.items():
        if orig_value is None or str(orig_value).strip() == "":
            continue
            
        key_lower = orig_key.lower().strip()
        value_str = str(orig_value).strip()
        
        # Check mapping
        if key_lower in FIELD_MAPPING:
            target_field = FIELD_MAPPING[key_lower]
            if target_field in std_record and not std_record[target_field]:
                std_record[target_field] = value_str
        else:
            # Fuzzy mapping fallback
            for pattern, target in FIELD_MAPPING.items():
                if pattern in key_lower or key_lower in pattern:
                    if target in std_record and not std_record[target]:
                        std_record[target] = value_str
                        break
    
    return std_record

def load_all_databases() -> List[Dict]:
    """Load and standardize all records from all database files"""
    all_records = []
    files = get_database_files()
    
    if not files:
        print(f"{Fore.RED}[!] No database files found!")
        return []
    
    print(f"{Fore.CYAN}[*] Loading {len(files)} database files...")
    
    for file_path in files:
        records = load_json_file(file_path)
        for record in records:
            std_record = standardize_record(record, file_path.name)
            # Only include if we have at least a name
            if std_record["Nama"]:
                all_records.append(std_record)
    
    print(f"{Fore.GREEN}[+] Loaded {len(all_records)} total records")
    return all_records

def is_full_name(query: str) -> bool:
    """Check if query is a full name (contains spaces)"""
    return ' ' in query.strip()

def match_nickname(record_name: str, query: str) -> bool:
    """Match nickname (partial match)"""
    query_upper = query.upper()
    record_upper = record_name.upper()
    
    # Direct substring match
    if query_upper in record_upper:
        return True
    
    # Fuzzy match for typos (threshold 80)
    if fuzz.partial_ratio(query_upper, record_upper) >= 80:
        return True
    
    # Check each word in record name
    record_words = record_upper.split()
    for word in record_words:
        if fuzz.ratio(query_upper, word) >= 85:
            return True
        if query_upper in word:
            return True
    
    return False

def match_full_name(record_name: str, query: str) -> bool:
    """Match full name (exact match)"""
    query_upper = query.upper().strip()
    record_upper = record_name.upper().strip()
    
    # Exact match
    if record_upper == query_upper:
        return True
    
    # Fuzzy match for small typos in full names (threshold 95)
    if fuzz.ratio(record_upper, query_upper) >= 95:
        return True
    
    return False

def search_database(records: List[Dict], query: str) -> List[Dict]:
    """Search records based on query"""
    query = query.strip()
    if not query:
        return []
    
    is_full = is_full_name(query)
    search_type = "FULL NAME" if is_full else "NICKNAME"
    
    print(f"{Fore.CYAN}[*] Search mode: {search_type} | Query: '{query}'")
    
    results = []
    seen = set()  # Avoid duplicates
    
    for record in records:
        record_name = record.get("Nama", "")
        if not record_name:
            continue
        
        # Create unique key for deduplication
        record_key = f"{record_name}|{record.get('NIK', '')}|{record.get('NIP', '')}"
        if record_key in seen:
            continue
        
        match = False
        if is_full:
            match = match_full_name(record_name, query)
        else:
            match = match_nickname(record_name, query)
        
        if match:
            seen.add(record_key)
            results.append(record)
    
    return results

def display_results(results: List[Dict], query: str):
    """Display search results in formatted table"""
    if not results:
        print(f"\n{Fore.RED}[!] No results found for '{query}'")
        return
    
    print(f"\n{Fore.GREEN}[+] Found {len(results)} result(s) for '{query}':")
    print(f"{Fore.CYAN}{'='*60}")
    
    for idx, record in enumerate(results, 1):
        source = record.pop("_source", "unknown")
        
        print(f"\n{Fore.YELLOW}[ Result #{idx} | Source: {source} ]{Style.RESET_ALL}")
        
        # Prepare table data
        table_data = []
        for field in REQUIRED_FIELDS:
            value = record.get(field, "")
            if value:  # Only show non-empty fields
                table_data.append([field, value])
        
        if table_data:
            print(tabulate(table_data, headers=["Field", "Value"], 
                          tablefmt="grid", maxcolwidths=[15, 50]))
        else:
            print(f"{Fore.RED}    No data fields available{Style.RESET_ALL}")
        
        if idx < len(results):
            print(f"{Fore.CYAN}{'-'*60}")

def main():
    """Main program loop"""
    clear_screen()
    print_banner()
    
    # Load databases
    print(f"\n{Fore.CYAN}[*] Initializing database...")
    records = load_all_databases()
    
    if not records:
        print(f"{Fore.RED}[!] No records loaded. Exiting.")
        return
    
    print(f"{Fore.GREEN}[+] Ready. Type 'exit' to quit.")
    
    while True:
        try:
            print(f"\n{Fore.YELLOW}┌─[SilentDox@Search]")
            query = input(f"{Fore.YELLOW}└──╼ {Fore.WHITE}").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print(f"{Fore.CYAN}[*] Shutting down SilentDox...")
                break
            
            if not query:
                continue
            
            results = search_database(records, query)
            display_results(results, query)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}[*] Interrupted. Exiting...")
            break
        except Exception as e:
            print(f"{Fore.RED}[!] Error: {e}")

if __name__ == "__main__":
    main()