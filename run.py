from app import create_app
from app.seed import seed_data
app=create_app()
@app.cli.command("seed")
def seed():
    seed_data();print("Seeded")

from app.seed_couple_features import seed_couple_features

@app.cli.command("seed-couple-features")
def seed_couple_features_command():
    seed_couple_features()
    print("Seeded couple features.")

    
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
