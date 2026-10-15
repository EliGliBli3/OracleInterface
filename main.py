from datetime import datetime
import oracle_engine as fscm

if __name__ == '__main__':
    fscm.prompt_login()

    start_time = datetime.now()

    # Trial fetch
    fscm.fetch_wos([
        "125433",
        "112830",
        "119932",
        "121052",
        "133828",
        "130664",
        "147040",
        "142653",
        "139575",
        "140222",
    ])

    end_time = datetime.now()

    print (f"Finished fetching in {(end_time-start_time).total_seconds()} seconds.")
