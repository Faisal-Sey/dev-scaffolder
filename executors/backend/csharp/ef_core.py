import argparse

def configure_ef_core(db_provider="SQL Server", enable_migrations=True):
    print(f"Configuring Entity Framework Core")
    print(f"Database Provider: {db_provider}")
    print(f"Enable Migrations: {enable_migrations}")
    # Placeholder for actual configuration logic

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EF Core Configurator")
    parser.add_argument("--db_provider", type=str, default="SQL Server")
    parser.add_argument("--enable_migrations", type=bool, default=True)
    args = parser.parse_args()
    
    configure_ef_core(args.db_provider, args.enable_migrations)
