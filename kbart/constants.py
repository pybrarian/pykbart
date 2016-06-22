RP1_FIELDS = (
    'publication_title', 'print_identifier', 'online_identifier',
    'date_first_issue_online', 'num_first_vol_online',
    'num_first_issue_online', 'date_last_issue_online',
    'num_last_vol_online', 'num_last_issue_online', 'title_url',
    'first_author', 'title_id', 'embargo_info',  'coverage_depth',
    'coverage_notes'
)

RP2_FIELDS = (
    'notes', 'publisher_name', 'publication_type',
    'date_monograph_published_print',
    'date_monograph_published_online', 'monograph_volume',
    'monograph_edition', 'first_editor',
    'parent_publication_title_id', 'preceding_publication_title_id',
    'access_type'
)

PROVIDER_FIELDS = {
    'oclc': (
        'publisher_name', 'location', 'title_notes',
        'staff_notes', 'vendor_id', 'oclc_collection_name',
        'oclc_collection_id', 'oclc_entry_id', 'oclc_linkscheme',
        'oclc_number', 'ACTION'
    ),
    'gale': (
        'series_title', 'series_number', 'description', 'audience',
        'frequency', 'format', 'referred_peer_re-viewed', 'country',
        'language', 'primary_subject'
    )
}

EMBARGO_CODES_TO_STRINGS = {
    'd': 'day(s)', 'm': 'month(s)', 'y': 'year(s)',
    'r': 'From {} {} ago to present',
    'p': 'Up to {} {} ago'
}
