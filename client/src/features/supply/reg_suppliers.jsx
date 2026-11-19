import { useState, useEffect} from 'react'
import { api } from '../../api/client'

function RegSuppliers() {
    const [suppliers, setSuppliers] = useState([])
    const [message, setMessage] = useState('')
    const [formData, setFormData] = useState({
        name: '',
        contact_person: '',
        email: '',
        phone: '',
        address: ''
    })

    //Fetch all registered suppliers
    const fetchSuppliers = async () => {
        try {
            const data = await api('/suppliers')
            setSuppliers(data)
        } catch (error) {
            console.error('Error fetching suppliers:', error)
            setMessage(error.message)
        }
    }
    
    //Fetch suppliers on component mount
    useEffect(() => {
        fetchSuppliers()
    }, [])
    
    //Handle form input changes
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }
    
    //Register a new supplier
    const handleSubmit = async (e) => {
        e.preventDefault()
        setMessage('')

        try {
            const data = await api('/register_supplier', {
                method: 'POST',
                body: JSON.stringify(formData)
            })
                 
            setSuppliers(prevSuppliers => [...prevSuppliers, data])
            setMessage('Supplier registered successfully.')

            setFormData({
                name: '',
                contact_person: '',
                email: '',
                phone: '',
                address: ''
            })
        } catch (error) {
            setMessage(error.message)
        }
    }
    
    //Delete a supplier
    const handleDelete = async (id) => {
        setMessage('')

        try {
            await api(`/delete_suppliers/${id}`,{
                method: 'DELETE'
            })
           
            setSuppliers(prevSuppliers => prevSuppliers.filter(supplier => supplier.id !== id))
            setMessage('Supplier deleted successfully.')
        } catch (error) {
            setMessage(error.message)
        }
    }

    return (
        <div className="suppliers-page">
            <h2>Register Suppliers</h2>
            <p>Manage your registered suppliers.</p>

            {message && <p className="message">{message}</p>}

            <form onSubmit={handleSubmit} className="supplier-form">
                <h3>Register New Supplier</h3>

                <input
                    type="text"
                    name="name"
                    placeholder="Supplier Name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                />

                <input
                    type="text"
                    name="contact_person"
                    placeholder="Contact Person"
                    value={formData.contact_person}
                    onChange={handleChange}
                    required
                />

                <input
                    type="email"
                    name="email"
                    placeholder="Email Address"
                    value={formData.email}
                    onChange={handleChange}
                    required
                />
                <input
                    type="tel"
                    name="phone"
                    placeholder="Phone Number"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                />
                <input
                    type="text"
                    name="address"
                    placeholder="Supplier Address"
                    value={formData.address}
                    onChange={handleChange}
                    required
                />
                <button type="submit">Register Supplier</button>
            </form>

            <div className="supplier-list">
                <h3>Supplier List</h3>

                {suppliers.length === 0 ? (
                    <p>No suppliers registered yet.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Contact Person</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Address</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {suppliers.map((supplier) => (
                                <tr key={supplier.id}>
                                    <td>{supplier.name}</td>
                                    <td>{supplier.contact_person}</td>
                                    <td>{supplier.email}</td>
                                    <td>{supplier.phone}</td>
                                    <td>{supplier.address}</td>
                                    <td>
                                        <button type="button" onClick={() => handleDelete(supplier.id)}>Delete</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default RegSuppliers
