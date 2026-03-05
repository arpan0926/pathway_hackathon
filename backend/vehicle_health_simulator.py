import time
import random
import psycopg2
import os
from datetime import datetime, timedelta
import numpy as np
import threading

class VehicleHealthSimulator:
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        
        # Initial conditions (healthy vehicle)
        self.engine_temp = 85.0  # Celsius
        self.engine_rpm = 1500
        self.oil_pressure = 45.0  # PSI
        self.coolant_level = 100.0  # Percent
        self.vibration = 2.0  # 0-10 scale
        self.brake_pad_mm = 12.0  # mm (new = 12mm, replace at 3mm)
        self.tire_pressure = 32.0  # PSI
        self.battery_voltage = 12.6  # Volts
        self.alternator_output = 14.2  # Volts
        
        # Wear accumulation over time
        self.total_km_driven = random.randint(10000, 50000)
        self.hours_since_oil_change = random.randint(0, 3000)
        self.hours_since_brake_check = random.randint(0, 5000)
        
    def simulate_driving_conditions(self, speed_kmph):
        """Simulate realistic wear and tear based on driving"""
        
        # Engine temperature increases with speed and load
        if speed_kmph > 80:
            self.engine_temp += random.uniform(0.5, 2.0)
            self.engine_rpm = random.randint(2500, 3500)
        elif speed_kmph > 40:
            self.engine_temp += random.uniform(0.1, 0.5)
            self.engine_rpm = random.randint(1800, 2500)
        else:
            self.engine_temp += random.uniform(-0.5, 0.2)
            self.engine_rpm = random.randint(1000, 1800)
        
        # Temperature naturally cools down when not overheating
        if self.engine_temp > 90:
            self.engine_temp -= random.uniform(0.0, 0.3)
        
        # Clamp temperature (85-115 range, overheating at 110+)
        self.engine_temp = max(75, min(120, self.engine_temp))
        
        # Oil pressure degrades over time
        self.oil_pressure -= random.uniform(0.0, 0.01)
        self.oil_pressure = max(20, min(50, self.oil_pressure))
        
        # Coolant slowly evaporates
        self.coolant_level -= random.uniform(0.0, 0.005)
        self.coolant_level = max(60, self.coolant_level)
        
        # Vibration increases with wear
        self.vibration += random.uniform(0.0, 0.01)
        self.vibration = min(10, self.vibration)
        
        # Brake pads wear down
        if speed_kmph > 0:
            self.brake_pad_mm -= random.uniform(0.0, 0.0005)
            self.brake_pad_mm = max(0, self.brake_pad_mm)
        
        # Tire pressure fluctuates
        self.tire_pressure += random.uniform(-0.1, 0.05)
        self.tire_pressure = max(25, min(35, self.tire_pressure))
        
        # Battery degrades slowly
        self.battery_voltage -= random.uniform(0.0, 0.001)
        self.battery_voltage = max(11.5, min(12.8, self.battery_voltage))
        
        # Simulate occasional failures
        if random.random() < 0.001:  # 0.1% chance per tick
            failure_type = random.choice(['oil_leak', 'coolant_leak', 'battery_drain'])
            if failure_type == 'oil_leak':
                self.oil_pressure -= 5
            elif failure_type == 'coolant_leak':
                self.coolant_level -= 10
            elif failure_type == 'battery_drain':
                self.battery_voltage -= 0.5
    
    def calculate_health_scores(self):
        """Calculate component health scores (0-100)"""
        
        # Engine health (temp, oil, coolant)
        temp_score = max(0, 100 - abs(self.engine_temp - 85) * 3)
        oil_score = (self.oil_pressure / 50) * 100
        coolant_score = self.coolant_level
        engine_health = (temp_score + oil_score + coolant_score) / 3
        
        # Brake health
        brake_health = (self.brake_pad_mm / 12) * 100
        
        # Tire health
        tire_health = max(0, 100 - abs(self.tire_pressure - 32) * 5)
        
        # Battery health
        battery_health = ((self.battery_voltage - 11.5) / (12.8 - 11.5)) * 100
        
        # Overall health (weighted average)
        overall_health = (
            engine_health * 0.4 + 
            brake_health * 0.3 + 
            tire_health * 0.2 + 
            battery_health * 0.1
        )
        
        return {
            'engine': engine_health,
            'brake': brake_health,
            'tire': tire_health,
            'battery': battery_health,
            'overall': overall_health
        }
    
    def predict_failures(self, health_scores):
        """Predict when failures will occur"""
        
        predictions = []
        
        # Engine overheating prediction
        if self.engine_temp > 105:
            predictions.append({
                'type': 'engine_overheating',
                'component': 'cooling_system',
                'days': 0,
                'urgency': 'critical',
                'recommendation': 'IMMEDIATE: Pull over and let engine cool. Check coolant level.'
            })
        elif self.engine_temp > 100:
            predictions.append({
                'type': 'engine_overheating_risk',
                'component': 'cooling_system',
                'days': 1,
                'urgency': 'high',
                'recommendation': 'Check cooling system within 24 hours. Monitor temperature closely.'
            })
        
        # Oil pressure failure
        if self.oil_pressure < 25:
            predictions.append({
                'type': 'oil_pressure_low',
                'component': 'lubrication_system',
                'days': 0,
                'urgency': 'critical',
                'recommendation': 'IMMEDIATE: Stop engine. Check oil level and add if needed.'
            })
        elif self.oil_pressure < 35:
            days_to_failure = int((self.oil_pressure - 25) / 0.5)
            predictions.append({
                'type': 'oil_pressure_declining',
                'component': 'lubrication_system',
                'days': days_to_failure,
                'urgency': 'medium',
                'recommendation': f'Schedule oil change within {days_to_failure} days.'
            })
        
        # Brake wear
        if self.brake_pad_mm < 3:
            predictions.append({
                'type': 'brake_pads_critical',
                'component': 'braking_system',
                'days': 0,
                'urgency': 'critical',
                'recommendation': 'IMMEDIATE: Replace brake pads. Vehicle unsafe to drive.'
            })
        elif self.brake_pad_mm < 5:
            days_to_failure = int((self.brake_pad_mm - 3) * 200)
            predictions.append({
                'type': 'brake_pads_worn',
                'component': 'braking_system',
                'days': days_to_failure,
                'urgency': 'high',
                'recommendation': f'Replace brake pads within {days_to_failure} days.'
            })
        
        # Tire pressure
        if self.tire_pressure < 28:
            predictions.append({
                'type': 'tire_pressure_low',
                'component': 'tires',
                'days': 0,
                'urgency': 'high',
                'recommendation': 'Inflate tires to 32 PSI immediately. Check for leaks.'
            })
        
        # Battery
        if self.battery_voltage < 11.8:
            predictions.append({
                'type': 'battery_weak',
                'component': 'electrical_system',
                'days': 3,
                'urgency': 'medium',
                'recommendation': 'Replace battery within 3 days to avoid starting issues.'
            })
        
        # Vibration (bearing wear)
        if self.vibration > 7:
            predictions.append({
                'type': 'bearing_wear',
                'component': 'drivetrain',
                'days': 7,
                'urgency': 'medium',
                'recommendation': 'Inspect wheel bearings and suspension within 7 days.'
            })
        
        return predictions


def get_db_connection():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"
    )
    return psycopg2.connect(db_url)


def get_current_speed(vehicle_id):
    """Get current speed from telemetry"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT speed_kmph FROM telemetry 
            WHERE vehicle_id = %s 
            ORDER BY ts DESC LIMIT 1
        """, (vehicle_id,))
        result = cur.fetchone()
        conn.close()
        return result[0] if result else 0
    except:
        return random.uniform(40, 60)


def insert_vehicle_health(vehicle_id, simulator, health_scores, predictions):
    """Insert health data into database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get shipment_id
        cur.execute("SELECT shipment_id FROM shipments WHERE vehicle_id = %s LIMIT 1", (vehicle_id,))
        result = cur.fetchone()
        shipment_id = result[0] if result else None
        
        # Insert health telemetry
        cur.execute("""
            INSERT INTO vehicle_health (
                vehicle_id, shipment_id, ts,
                engine_temp_celsius, engine_rpm, oil_pressure_psi, coolant_level_percent,
                vibration_level, brake_pad_thickness_mm, tire_pressure_psi,
                battery_voltage, alternator_output,
                engine_health_score, brake_health_score, tire_health_score, 
                battery_health_score, overall_health_score,
                predicted_failure_type, predicted_failure_days, maintenance_urgency
            ) VALUES (
                %s, %s, NOW(),
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """, (
            vehicle_id, shipment_id,
            simulator.engine_temp, simulator.engine_rpm, simulator.oil_pressure, simulator.coolant_level,
            simulator.vibration, simulator.brake_pad_mm, simulator.tire_pressure,
            simulator.battery_voltage, simulator.alternator_output,
            health_scores['engine'], health_scores['brake'], health_scores['tire'],
            health_scores['battery'], health_scores['overall'],
            predictions[0]['type'] if predictions else None,
            predictions[0]['days'] if predictions else None,
            predictions[0]['urgency'] if predictions else 'low'
        ))
        
        # Insert maintenance alerts for critical predictions
        for pred in predictions:
            if pred['urgency'] in ['critical', 'high']:
                # Check if alert already exists
                cur.execute("""
                    SELECT alert_id FROM maintenance_alerts 
                    WHERE vehicle_id = %s AND alert_type = %s AND is_active = true
                """, (vehicle_id, pred['type']))
                
                if not cur.fetchone():
                    predicted_date = datetime.now() + timedelta(days=pred['days'])
                    cur.execute("""
                        INSERT INTO maintenance_alerts (
                            vehicle_id, shipment_id, alert_type, component, severity,
                            predicted_failure_date, recommendation, is_active
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, true)
                    """, (
                        vehicle_id, shipment_id, pred['type'], pred['component'],
                        pred['urgency'], predicted_date, pred['recommendation']
                    ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"❌ DB Error [{vehicle_id}]: {e}")


def simulate_vehicle_health(vehicle_id):
    """Run continuous health simulation for a vehicle"""
    simulator = VehicleHealthSimulator(vehicle_id)
    
    print(f"🔧 Starting health monitoring for {vehicle_id}")
    
    while True:
        try:
            # Get current driving speed
            speed = get_current_speed(vehicle_id)
            
            # Simulate wear and tear
            simulator.simulate_driving_conditions(speed)
            
            # Calculate health scores
            health_scores = simulator.calculate_health_scores()
            
            # Predict failures
            predictions = simulator.predict_failures(health_scores)
            
            # Log status
            status_icon = "🟢" if health_scores['overall'] > 80 else "🟡" if health_scores['overall'] > 50 else "🔴"
            print(f"{status_icon} [{vehicle_id}] Health: {health_scores['overall']:.0f}% | "
                  f"Temp: {simulator.engine_temp:.1f}°C | Oil: {simulator.oil_pressure:.0f}psi | "
                  f"Brake: {simulator.brake_pad_mm:.1f}mm")
            
            if predictions:
                for pred in predictions:
                    if pred['urgency'] in ['critical', 'high']:
                        print(f"   ⚠️  {pred['type']}: {pred['recommendation']}")
            
            # Insert to database
            insert_vehicle_health(vehicle_id, simulator, health_scores, predictions)
            
            time.sleep(5)  # Update every 5 seconds
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    print("\n🔧 Vehicle Health Monitoring System")
    print("=" * 60)
    
    # Wait for DB
    print("⏳ Waiting for database...")
    for attempt in range(10):
        try:
            conn = get_db_connection()
            conn.close()
            print("✅ Database connected!")
            break
        except:
            print(f"   Attempt {attempt + 1}/10...")
            time.sleep(3)
    
    # Run health simulation for all 4 vehicles in parallel
    threads = [
        threading.Thread(target=simulate_vehicle_health, args=("VH001",), daemon=True),
        threading.Thread(target=simulate_vehicle_health, args=("VH002",), daemon=True),
        threading.Thread(target=simulate_vehicle_health, args=("VH003",), daemon=True),
        threading.Thread(target=simulate_vehicle_health, args=("VH004",), daemon=True),
    ]
    
    for t in threads:
        t.start()
        time.sleep(0.5)
    
    print("\n✅ All 4 vehicle health monitors running!")
    print("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Health monitoring stopped")