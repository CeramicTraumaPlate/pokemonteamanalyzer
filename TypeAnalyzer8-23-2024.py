import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict

# Define the type chart
type_chart = {
    'Normal': {'weak': ['Fighting'], 'resist': [], 'immune': ['Ghost']},
    'Fire': {'weak': ['Water', 'Rock', 'Ground'], 'resist': ['Fire', 'Grass', 'Ice', 'Bug', 'Steel', 'Fairy'], 'immune': []},
    'Water': {'weak': ['Electric', 'Grass'], 'resist': ['Fire', 'Water', 'Ice', 'Steel'], 'immune': []},
    'Electric': {'weak': ['Ground'], 'resist': ['Electric', 'Flying', 'Steel'], 'immune': []},
    'Grass': {'weak': ['Fire', 'Ice', 'Poison', 'Flying', 'Bug'], 'resist': ['Water', 'Electric', 'Grass', 'Ground'], 'immune': []},
    'Ice': {'weak': ['Fire', 'Fighting', 'Rock', 'Steel'], 'resist': ['Ice'], 'immune': []},
    'Fighting': {'weak': ['Flying', 'Psychic', 'Fairy'], 'resist': ['Bug', 'Rock', 'Dark'], 'immune': []},
    'Poison': {'weak': ['Ground', 'Psychic'], 'resist': ['Grass', 'Fighting', 'Poison', 'Bug', 'Fairy'], 'immune': []},
    'Ground': {'weak': ['Water', 'Grass', 'Ice'], 'resist': ['Poison', 'Rock'], 'immune': ['Electric']},
    'Flying': {'weak': ['Electric', 'Ice', 'Rock'], 'resist': ['Grass', 'Fighting', 'Bug'], 'immune': ['Ground']},
    'Psychic': {'weak': ['Bug', 'Ghost', 'Dark'], 'resist': ['Fighting', 'Psychic'], 'immune': []},
    'Bug': {'weak': ['Fire', 'Flying', 'Rock'], 'resist': ['Grass', 'Fighting', 'Ground'], 'immune': []},
    'Rock': {'weak': ['Water', 'Grass', 'Fighting', 'Ground', 'Steel'], 'resist': ['Normal', 'Fire', 'Poison', 'Flying'], 'immune': []},
    'Ghost': {'weak': ['Ghost', 'Dark'], 'resist': ['Poison', 'Bug'], 'immune': ['Normal', 'Fighting']},
    'Dragon': {'weak': ['Ice', 'Dragon', 'Fairy'], 'resist': ['Fire', 'Water', 'Electric', 'Grass'], 'immune': []},
    'Dark': {'weak': ['Fighting', 'Bug', 'Fairy'], 'resist': ['Ghost', 'Dark'], 'immune': ['Psychic']},
    'Steel': {'weak': ['Fire', 'Fighting', 'Ground'], 'resist': ['Normal', 'Grass', 'Ice', 'Flying', 'Psychic', 'Bug', 'Rock', 'Dragon', 'Steel', 'Fairy'], 'immune': ['Poison']},
    'Fairy': {'weak': ['Poison', 'Steel'], 'resist': ['Fighting', 'Bug', 'Dark'], 'immune': ['Dragon']}
}

# Function to calculate the team's weaknesses, resistances, and immunities
def calculate_team_matchups(team):
    weaknesses = {type_name: 0 for type_name in type_chart}
    resistances = {type_name: 0 for type_name in type_chart}
    immunities = {type_name: 0 for type_name in type_chart}

    for pokemon in team:
        type1, type2, specific_immunities = pokemon
        types = [type1]
        if type2:
            types.append(type2)

        # Check specific immunities first
        for immune_type in specific_immunities:
            immunities[immune_type] += 1

        # Calculate the effect of dual typings
        type_effectiveness = {type_name: 1.0 for type_name in type_chart}

        for poke_type in types:
            for weak_type in type_chart[poke_type]['weak']:
                if weak_type not in specific_immunities:
                    type_effectiveness[weak_type] *= 2
            for resist_type in type_chart[poke_type]['resist']:
                type_effectiveness[resist_type] *= 0.5
            for immune_type in type_chart[poke_type]['immune']:
                type_effectiveness[immune_type] *= 0.0

        # Count weaknesses, resistances, and immunities
        for type_name, effectiveness in type_effectiveness.items():
            if effectiveness == 4.0:  # Quadruple weakness
                weaknesses[type_name] += 2
            elif effectiveness == 2.0:
                weaknesses[type_name] += 1
            elif effectiveness == 0.5:
                resistances[type_name] += 1
            elif effectiveness == 0.0:
                immunities[type_name] += 1
    
    return weaknesses, resistances, immunities

# Intelligent recommendation function
def recommend_types_intelligently(weaknesses, resistances, immunities):
    type_chart_keys = sorted(type_chart.keys())

    # Calculate net weaknesses by subtracting resistances and immunities from weaknesses
    net_weaknesses = {type_name: max(0, weaknesses[type_name] - resistances[type_name] - immunities[type_name]) for type_name in type_chart_keys}

    # Identify the most common weakness
    common_weaknesses = {type_name: weaknesses[type_name] for type_name, count in net_weaknesses.items() if count > 0}
    if not common_weaknesses:
        return ["Your team has no major weaknesses. No additional types are necessary."]

    most_common_weakness = max(common_weaknesses, key=common_weaknesses.get)

    # Dictionary to score types based on how much they cover vulnerabilities, with priority to the most common weakness
    type_scores = defaultdict(int)

    for type_name in type_chart_keys:
        # Calculate how this type would mitigate the most common weakness
        resist_common = most_common_weakness in type_chart[type_name]['resist']
        immune_common = most_common_weakness in type_chart[type_name]['immune']

        # Calculate how this type would mitigate other vulnerabilities
        resist_count = sum(1 for weak_type in net_weaknesses if type_name in type_chart[weak_type]['resist'])
        immune_count = sum(1 for weak_type in net_weaknesses if type_name in type_chart[weak_type]['immune'])
        new_weakness_count = sum(1 for poke_type in type_chart[type_name]['weak'] if net_weaknesses[poke_type] > 0)

        # Skip types with no resistances and no useful immunities
        if resist_count == 0 and immune_count == 0:
            continue

        # Score the type: prioritize the most common weakness coverage
        type_scores[type_name] = 5 * immune_common + 3 * resist_common + immune_count + resist_count - new_weakness_count

    # Sort types based on their score
    sorted_type_scores = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)

    # Suggest top 5 types with sensible messages
    recommendations = []
    for type_name, score in sorted_type_scores[:5]:
        if score > 0:
            # Calculate how many actual weaknesses this type mitigates
            mitigated_weaknesses = sum(1 for weak_type in net_weaknesses if type_name in type_chart[weak_type]['resist'] or type_name in type_chart[weak_type]['immune'])
            recommendations.append(f"Adding a {type_name} type Pokémon would mitigate {mitigated_weaknesses} weaknesses.")

    # If no beneficial types were found, provide a fallback message
    if not recommendations:
        recommendations.append("No single type can greatly improve your team, consider dual-type Pokémon or coverage moves.")

    # Suggest top 5 dual-type combinations with sensible messages
    dual_type_scores = defaultdict(int)
    for type1 in type_chart_keys:
        for type2 in type_chart_keys:
            if type1 != type2 and (type2, type1) not in dual_type_scores:
                # Calculate combined resistances, weaknesses, and immunities
                combined_resistances = set(type_chart[type1]['resist']) | set(type_chart[type2]['resist'])
                combined_immunities = set(type_chart[type1]['immune']) | set(type_chart[type2]['immune'])
                combined_weaknesses = set(type_chart[type1]['weak']) | set(type_chart[type2]['weak'])

                # Mitigation for the most common weakness
                resist_common = most_common_weakness in combined_resistances
                immune_common = most_common_weakness in combined_immunities

                # Calculate how this dual type would mitigate other vulnerabilities
                resist_count = sum(1 for weak_type in net_weaknesses if weak_type in combined_resistances)
                immune_count = sum(1 for weak_type in net_weaknesses if weak_type in combined_immunities)
                new_weakness_count = sum(1 for poke_type in combined_weaknesses if net_weaknesses[poke_type] > 0)

                # Skip dual-types with no resistances and no useful immunities
                if resist_count == 0 and immune_count == 0:
                    continue

                # Score the dual type: prioritize the most common weakness coverage
                dual_type_scores[(type1, type2)] = 5 * immune_common + 3 * resist_common + immune_count + resist_count - new_weakness_count

    # Sort dual-type scores based on their score
    sorted_dual_type_scores = sorted(dual_type_scores.items(), key=lambda x: x[1], reverse=True)

    # Suggest top 5 dual-type combinations with sensible messages
    dual_recommendations = []
    for (type1, type2), score in sorted_dual_type_scores[:5]:
        if score > 0:
            # Calculate how many actual weaknesses this dual type mitigates
            mitigated_weaknesses = sum(1 for weak_type in net_weaknesses if weak_type in set(type_chart[type1]['resist']) | set(type_chart[type2]['resist']) or weak_type in set(type_chart[type1]['immune']) | set(type_chart[type2]['immune']))
            dual_recommendations.append(f"Adding a {type1}/{type2} type Pokémon would mitigate {mitigated_weaknesses} weaknesses.")

    if dual_recommendations:
        recommendations.append("\nDual-Type Recommendations:\n" + "\n".join(dual_recommendations))
    else:
        recommendations.append("No dual-type Pokémon significantly improve your team.")

    return recommendations



# Function to rate the team
def rate_team(weaknesses, resistances, immunities):
    total_weaknesses = sum(weaknesses.values())
    total_resistances = sum(resistances.values())
    total_immunities = sum(immunities.values())

   
  # Calculate the net weakness score
    net_weaknesses = total_weaknesses - total_resistances - total_immunities

    # Apply stricter rating criteria
    if total_weaknesses > 10 or net_weaknesses > 10:
        return "Bad"
    elif total_weaknesses > 7 or net_weaknesses > 7:
        return "Below Average"
    elif total_weaknesses > 4 or net_weaknesses > 4:
        return "Average"
    elif total_weaknesses > 2 or net_weaknesses > 2:
        return "Above Average"
    else:
        return "Excellent"

# GUI code
def create_gui():
    root = tk.Tk()
    root.title("Pokemon Team Analyzer")

    types = sorted(type_chart.keys())
    immunities = sorted(type_chart.keys()) + [""]
    blank_option = ""

    team_vars = []

    for i in range(6):
        tk.Label(root, text=f"Pokemon {i + 1} Type 1:").grid(row=i, column=0, padx=10, pady=5)
        type1_var = tk.StringVar(value=blank_option)
        type1_menu = ttk.Combobox(root, textvariable=type1_var, values=[blank_option] + types)
        type1_menu.grid(row=i, column=1)

        tk.Label(root, text=f"Pokemon {i + 1} Type 2:").grid(row=i, column=2, padx=10, pady=5)
        type2_var = tk.StringVar(value=blank_option)
        type2_menu = ttk.Combobox(root, textvariable=type2_var, values=[blank_option] + types)
        type2_menu.grid(row=i, column=3)

        tk.Label(root, text=f"Pokemon {i + 1} Immunities:").grid(row=i, column=4, padx=10, pady=5)
        immunities_var = tk.StringVar(value=blank_option)
        immunities_menu = ttk.Combobox(root, textvariable=immunities_var, values=[blank_option] + immunities)
        immunities_menu.grid(row=i, column=5)

        team_vars.append((type1_var, type2_var, immunities_var))

    def analyze_team():
        team = []
        for type1_var, type2_var, immunities_var in team_vars:
            type1 = type1_var.get() or None
            type2 = type2_var.get() or None

            # Check for duplicate types
            if type1 and type2 and type1 == type2:
                messagebox.showwarning("Warning", f"Pokemon with Type 1 as {type1} and Type 2 as {type2} are the same. Please choose different types.")
                return

            specific_immunities = [immunities_var.get()] if immunities_var.get() and immunities_var.get() != blank_option else []
            if type1:
                team.append((type1, type2, specific_immunities))

        if not team:
            messagebox.showerror("Error", "Please select at least one Pokemon.")
            return

        weaknesses, resistances, immunities = calculate_team_matchups(team)

        # Sort the output by the number of weaknesses, resistances, and immunities
        sorted_weaknesses = sorted(weaknesses.items(), key=lambda x: x[1], reverse=True)
        sorted_resistances = sorted(resistances.items(), key=lambda x: x[1], reverse=True)
        sorted_immunities = sorted(immunities.items(), key=lambda x: x[1], reverse=True)

        # Build result text
        result_text = "Weaknesses:\n" + "\n".join([f"{type_name}: {count}" for type_name, count in sorted_weaknesses if count > 0])
        result_text += "\n\nResistances:\n" + "\n".join([f"{type_name}: {count}" for type_name, count in sorted_resistances if count > 0])
        result_text += "\n\nImmunities:\n" + "\n".join([f"{type_name}: {count}" for type_name, count in sorted_immunities if count > 0])

        recommendations = recommend_types_intelligently(weaknesses, resistances, immunities)
        result_text += "\n\nRecommendations:\n" + "\n".join(recommendations)

        team_rating = rate_team(weaknesses, resistances, immunities)
        result_text += f"\n\nTeam Rating: {team_rating}"

        messagebox.showinfo("Team Analysis", result_text)

    def reset_fields():
        for type1_var, type2_var, immunities_var in team_vars:
            type1_var.set(blank_option)
            type2_var.set(blank_option)
            immunities_var.set(blank_option)

    # Place buttons
    analyze_button = ttk.Button(root, text="Analyze Team", command=analyze_team)
    analyze_button.grid(row=7, column=5, padx=10, pady=10, sticky='e')

    reset_button = ttk.Button(root, text="Reset", command=reset_fields)
    reset_button.grid(row=7, column=0, padx=10, pady=10, sticky='w')

    root.mainloop()

if __name__ == "__main__":
    create_gui()
