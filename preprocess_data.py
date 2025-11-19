"""
Data Preprocessing Script for UAE Donations
This script processes the raw donation data and adds:
1. Hijri calendar dates and information
2. English translations of donation types
3. Islamic events identification
"""

import pandas as pd
from pathlib import Path
from hijri_converter import Hijri, Gregorian
from deep_translator import GoogleTranslator
import time
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_FILE = Path('data/General_Donation.csv')
OUTPUT_FILE = Path('data/General_Donation_Processed.csv')

# ============================================================================
# HIJRI CALENDAR FUNCTIONS
# ============================================================================

def get_hijri_date(gregorian_date):
    """Convert Gregorian date to Hijri date."""
    try:
        g = Gregorian(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        h = g.to_hijri()
        return h
    except:
        return None

def is_ramadan(gregorian_date):
    """Check if a Gregorian date falls in Ramadan."""
    hijri = get_hijri_date(gregorian_date)
    if hijri:
        return hijri.month == 9
    return False

def get_hijri_month_name(month_num):
    """Get Hijri month name."""
    months = {
        1: 'Muharram', 2: 'Safar', 3: 'Rabi al-Awwal', 4: 'Rabi al-Thani',
        5: 'Jumada al-Awwal', 6: 'Jumada al-Thani', 7: 'Rajab', 8: 'Shaban',
        9: 'Ramadan', 10: 'Shawwal', 11: 'Dhul Qadah', 12: 'Dhul Hijjah'
    }
    return months.get(month_num, 'Unknown')

def identify_islamic_events(gregorian_date):
    """Identify Islamic events for a given date."""
    hijri = get_hijri_date(gregorian_date)
    if not hijri:
        return None
    
    if hijri.month == 9:  # Ramadan
        if 1 <= hijri.day <= 10:
            return 'Ramadan (First 10 Days)'
        elif 11 <= hijri.day <= 20:
            return 'Ramadan (Middle 10 Days)'
        else:
            return 'Ramadan (Last 10 Days)'
    elif hijri.month == 10 and hijri.day <= 3:
        return 'Eid al-Fitr'
    elif hijri.month == 12 and 8 <= hijri.day <= 13:
        return 'Hajj & Eid al-Adha'
    elif hijri.month == 1 and hijri.day == 10:
        return 'Day of Ashura'
    elif hijri.month == 3 and hijri.day == 12:
        return 'Mawlid al-Nabi'
    
    return None

def get_ramadan_period(gregorian_date):
    """Get specific Ramadan period."""
    hijri = get_hijri_date(gregorian_date)
    if not hijri or hijri.month != 9:
        return None
    
    if 1 <= hijri.day <= 10:
        return 'First 10 Days'
    elif 11 <= hijri.day <= 20:
        return 'Middle 10 Days'
    else:
        return 'Last 10 Days'

# ============================================================================
# TRANSLATION FUNCTIONS
# ============================================================================

def create_translation_cache():
    """Create a translation cache to avoid repeated API calls."""
    # Common donation types in Arabic with their translations
    common_translations = {
        'أيتام خارج الدولة': 'Orphans Outside the Country',
        'سقيا الماء': 'Water Supply',
        'ادعم طفلا': 'Support a Child',
        'أمل جديد': 'New Hope',
        'كفالة يتيم': 'Orphan Sponsorship',
        'صدقة جارية': 'Ongoing Charity',
        'بناء مسجد': 'Mosque Construction',
        'زكاة المال': 'Zakat al-Mal',
        'إفطار صائم': 'Breaking Fast for Fasting Person',
        'كسوة العيد': "Eid Clothing",
        'علاج مريض': 'Patient Treatment',
        'بناء بئر': 'Well Construction',
        'مساعدة عائلة': 'Family Assistance',
        'تعليم طالب': 'Student Education',
        'دعم مشروع': 'Project Support',
    }
    return common_translations

def translate_text(text, translator, translation_cache):
    """Translate text from Arabic to English with caching."""
    if pd.isna(text) or text == '':
        return None
    
    # Check cache first
    if text in translation_cache:
        return translation_cache[text]
    
    try:
        # Translate using Google Translator
        translated = translator.translate(text)
        translation_cache[text] = translated
        time.sleep(0.1)  # Rate limiting
        return translated
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        return text  # Return original if translation fails

# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

def process_donation_data():
    """Main function to process donation data."""
    print("=" * 80)
    print("UAE DONATIONS DATA PREPROCESSING")
    print("=" * 80)
    print(f"\nStarting preprocessing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load raw data
    print(f"\n[1/5] Loading raw data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE, encoding='utf-8')
    print(f"   ✓ Loaded {len(df):,} records")
    
    # Convert and validate data types
    print("\n[2/5] Processing dates and amounts...")
    df['donationdate'] = pd.to_datetime(df['donationdate'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Remove invalid records
    before_clean = len(df)
    df = df.dropna(subset=['donationdate', 'amount'])
    after_clean = len(df)
    print(f"   ✓ Removed {before_clean - after_clean:,} invalid records")
    print(f"   ✓ {after_clean:,} valid records remaining")
    
    # Filter out incomplete years (2018 and 2025)
    df['year'] = df['donationdate'].dt.year
    before_filter = len(df)
    df = df[(df['year'] >= 2019) & (df['year'] <= 2024)]
    after_filter = len(df)
    print(f"   ✓ Filtered out {before_filter - after_filter:,} records from incomplete years (2018, 2025)")
    print(f"   ✓ {after_filter:,} records from complete years (2019-2024) remaining")
    
    # Extract time dimensions
    print("\n[3/5] Extracting time dimensions...")
    df['year'] = df['donationdate'].dt.year
    df['month'] = df['donationdate'].dt.month
    df['month_name'] = df['donationdate'].dt.strftime('%B')
    df['quarter'] = df['donationdate'].dt.quarter
    df['day'] = df['donationdate'].dt.day
    df['weekday'] = df['donationdate'].dt.day_name()
    df['week'] = df['donationdate'].dt.isocalendar().week
    df['hour'] = df['donationdate'].dt.hour
    df['date'] = df['donationdate'].dt.date
    print("   ✓ Extracted Gregorian calendar dimensions")
    
    # Add Hijri calendar information
    print("\n[4/5] Adding Hijri calendar information...")
    print("   Processing Hijri dates (this may take a moment)...")
    
    # Process in batches for progress tracking
    batch_size = 10000
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    hijri_data = []
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"   Processing batch {batch_num}/{total_batches}...", end='\r')
        
        for _, row in batch.iterrows():
            date = row['donationdate'].date()
            hijri = get_hijri_date(date)
            
            if hijri:
                hijri_data.append({
                    'hijri_year': hijri.year,
                    'hijri_month': hijri.month,
                    'hijri_day': hijri.day,
                    'hijri_month_name': get_hijri_month_name(hijri.month),
                    'is_ramadan': hijri.month == 9,
                    'islamic_event': identify_islamic_events(date),
                    'ramadan_period': get_ramadan_period(date) if hijri.month == 9 else None
                })
            else:
                hijri_data.append({
                    'hijri_year': None,
                    'hijri_month': None,
                    'hijri_day': None,
                    'hijri_month_name': None,
                    'is_ramadan': False,
                    'islamic_event': None,
                    'ramadan_period': None
                })
    
    print(f"\n   ✓ Processed Hijri dates for all {len(df):,} records")
    
    # Add Hijri columns to dataframe
    hijri_df = pd.DataFrame(hijri_data)
    df = pd.concat([df, hijri_df], axis=1)
    
    # Count Ramadan records
    ramadan_count = df['is_ramadan'].sum()
    ramadan_pct = (ramadan_count / len(df)) * 100
    print(f"   ✓ Identified {ramadan_count:,} Ramadan donations ({ramadan_pct:.1f}%)")
    
    # Translate donation types
    print("\n[5/5] Translating donation types to English...")
    translator = GoogleTranslator(source='ar', target='en')
    translation_cache = create_translation_cache()
    
    unique_types = df['donationtype'].unique()
    print(f"   Found {len(unique_types)} unique donation types")
    print("   Translating (this may take a few minutes)...")
    
    # Translate unique types first
    for idx, donation_type in enumerate(unique_types, 1):
        if pd.notna(donation_type):
            print(f"   Translating {idx}/{len(unique_types)}: {donation_type[:30]}...", end='\r')
            translate_text(donation_type, translator, translation_cache)
    
    print(f"\n   ✓ Completed translation of {len(translation_cache)} unique types")
    
    # Apply translations to dataframe
    df['donationtype_en'] = df['donationtype'].apply(
        lambda x: translation_cache.get(x, x) if pd.notna(x) else None
    )
    
    # Reorder columns for better readability
    column_order = [
        'id', 'donationdate', 'amount', 
        'donationtype', 'donationtype_en',
        'year', 'month', 'month_name', 'quarter', 'day', 'weekday', 'week', 'hour', 'date',
        'hijri_year', 'hijri_month', 'hijri_day', 'hijri_month_name',
        'is_ramadan', 'ramadan_period', 'islamic_event'
    ]
    
    df = df[column_order]
    
    # Save processed data
    print(f"\n[6/6] Saving processed data to {OUTPUT_FILE}...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"   ✓ Saved {len(df):,} processed records")
    
    # Display summary statistics
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    print(f"\nTotal Records:           {len(df):,}")
    print(f"Date Range:              {df['donationdate'].min()} to {df['donationdate'].max()}")
    print(f"Total Amount:            AED {df['amount'].sum():,.2f}")
    print(f"Average Donation:        AED {df['amount'].mean():,.2f}")
    print(f"\nRamadan Donations:       {ramadan_count:,} ({ramadan_pct:.1f}%)")
    print(f"Ramadan Amount:          AED {df[df['is_ramadan'] == True]['amount'].sum():,.2f}")
    print(f"Non-Ramadan Amount:      AED {df[df['is_ramadan'] == False]['amount'].sum():,.2f}")
    print(f"\nUnique Donation Types:   {df['donationtype'].nunique()}")
    print(f"Unique Donors:           {df['id'].nunique():,}")
    
    # Display Islamic events summary
    events = df[df['islamic_event'].notna()]['islamic_event'].value_counts()
    if len(events) > 0:
        print(f"\nIslamic Events Identified:")
        for event, count in events.items():
            print(f"  - {event}: {count:,} donations")
    
    print(f"\n✓ Processing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return df

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    try:
        processed_df = process_donation_data()
        print("\n✓ SUCCESS: Data preprocessing completed successfully!")
        print(f"✓ Processed file saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"\n✗ ERROR: Processing failed with error: {e}")
        import traceback
        traceback.print_exc()
